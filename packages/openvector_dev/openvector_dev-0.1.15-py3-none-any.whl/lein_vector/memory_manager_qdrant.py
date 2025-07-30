import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from lein_vector.bases.memory_manager_abc import MemoryManagerABC
from lein_vector.schemas.chunk import Chunk, ChunkPayload


class MemoryManagerQdrant(MemoryManagerABC):
    def __init__(self, qdrant_adapter, embedding_provider, archive_storage=None):
        self.qdrant = qdrant_adapter
        self.embed = embedding_provider
        self.archive = archive_storage  # твой модуль S3/minio (интерфейс: save(user_id, List[ChunkPayload]), load(user_id) -> List[ChunkPayload])

    async def upsert_chunk(self, user_id: int, bot: str, chunk: Chunk) -> None:
        assert chunk.bot == bot
        embedding = await self.embed.get_embedding(chunk.text)
        await self.qdrant.upsert(chunk.chunk_id, embedding, chunk.to_payload())

    async def upsert_chunk_with_vector(
        self, chunk: Chunk, embedding: list[float]
    ) -> None:
        await self.qdrant.upsert(chunk.chunk_id, embedding, chunk.to_payload())

    async def upsert_chunks(self, user_id: int, bot: str, chunks: list[Chunk]) -> None:
        for c in chunks:
            if c.bot != bot:
                raise ValueError(f"chunk.bot ({c.bot}) != bot ({bot})")
        texts = [c.text for c in chunks]
        embeddings = await self.embed.get_embeddings(texts)
        points = [
            {"point_id": c.chunk_id, "embedding": emb, "payload": c.to_payload()}
            for c, emb in zip(chunks, embeddings)
        ]
        await self.qdrant.upsert_batch(points)

    async def retrieve_by_embedding(
        self,
        user_id: int,
        embedding: list[float],
        *,
        bot: str,
        topk: int = 3,
        filter_: dict[str, Any] = None,
        score_threshold: float | None = None,
    ) -> list[ChunkPayload]:
        q_filter = {"user_id": user_id, "bot": bot}
        if filter_:
            q_filter.update(filter_)
        return await self.qdrant.search(embedding, q_filter, topk, score_threshold)

    async def retrieve_by_embeddings(
        self,
        bot: str,
        user_id: int,
        embeddings: list[list[float]],
        *,
        topk: int = 3,
        filter_: dict[str, Any] | None = None,
        score_threshold: float | None = None,
    ) -> list[list[ChunkPayload]]:
        """
        Возвращает список результатов для каждого Embedding.
        На выходе: [[ChunkPayload, …] для emb-0, [ChunkPayload, …] для emb-1, …]
        """
        q_filter = {"user_id": user_id, "bot": bot}
        if filter_:
            q_filter.update(filter_)

        if hasattr(self.qdrant, "search_batch"):
            return await self.qdrant.search_batch(
                query_vectors=embeddings,
                query_filter=q_filter,
                topk=topk,
                score_threshold=score_threshold,
            )

        async def _one(e):
            return await self.qdrant.search(e, q_filter, topk, score_threshold)

        return await asyncio.gather(*[_one(e) for e in embeddings])

    # ToDO: filter
    async def retrieve_by_type(
        self, user_id: int, bot: str, chunk_type: str, topk: int = 3
    ) -> list[ChunkPayload]:
        # Лучше использовать scroll по фильтру
        filter_ = {"user_id": user_id, "bot": bot, "chunk_type": chunk_type}
        return await self.qdrant.get_all_chunks_with_filter(filter_)

    async def merge_old_chunks(
            self,
            user_id: int,
            bot: str,
            chunk_type: str,
            n: int = 5,
    ) -> tuple[str | None, list[UUID]]:
        """
        Собрать n старых чанков и вернуть:
          • merged_text — склеенные сообщения c ролями,
          • used_ids    — UUID этих чанков.

        Если чанков меньше n — вернётся (None, []).
        """
        chunks = await self.qdrant.get_n_oldest_chunks(user_id, bot, chunk_type, n)
        if len(chunks) < n:
            return None, []

        def _ensure_role(txt: str, default_role: str = "gf") -> str:
            # если строка уже начинается с 'role: ', оставляем как есть
            if txt.split(":", 1)[0] in {"user", "gf", "assistant"}:
                return txt
            return f"{default_role}: {txt}"

        merged_text = "\n".join(_ensure_role(c.text) for c in chunks)
        used_ids = [c.chunk_id for c in chunks]

        return merged_text, used_ids

    async def archive_user(self, user_id: int, bot: str) -> None:
        all_chunks = await self.qdrant.get_all_chunks(user_id, bot)
        await self.archive.save(user_id, bot, all_chunks)
        await self.delete_all(user_id, bot)

    async def restore_user(self, user_id: int, bot: str) -> None:
        chunks = await self.archive.load(user_id, bot)
        await self.upsert_chunks(
            user_id,
            [
                Chunk(**c.dict(), last_hit=datetime.now(UTC), hit_count=0, bot=bot)
                for c in chunks
            ],
        )

    async def delete_chunk(self, user_id: int, bot: str, chunk_id: UUID) -> None:
        await self.qdrant.delete(chunk_id)

    async def delete_chunks(
        self, user_id: int, bot: str, chunk_ids: list[UUID]
    ) -> None:
        await self.qdrant.delete_batch(chunk_ids)

    async def delete_all(self, user_id: int, bot: str) -> None:
        all_chunks = await self.qdrant.get_all_chunks(user_id, bot)
        await self.delete_chunks(user_id, bot, [c.chunk_id for c in all_chunks])

    async def retrieve_filtered(
        self, user_id: int, bot: str, filter_: dict[str, Any], topk: int = 10
    ) -> list[ChunkPayload]:
        raise NotImplementedError
        q_filter = {"user_id": user_id, "bot": bot}
        q_filter.update(filter_)
        return await self.qdrant.get_all_chunks_with_filter(q_filter, topk=topk)

    @staticmethod
    def _next_type(chunk_type: str) -> str:
        # Логика типа next_type
        mapping = {"type0": "type1", "type1": "type2"}
        return mapping.get(chunk_type, "summary")
