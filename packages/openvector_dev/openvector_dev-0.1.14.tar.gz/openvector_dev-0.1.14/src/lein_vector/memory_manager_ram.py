from datetime import UTC, datetime
from uuid import UUID, uuid4

from lein_vector.bases.memory_manager_abc import MemoryManagerABC
from lein_vector.schemas.chunk import Chunk


class MemoryManagerRAM(MemoryManagerABC):
    def __init__(self):
        self._data: dict[int, dict[UUID, Chunk]] = {}
        self._archive: dict[int, dict[UUID, Chunk]] = {}

    async def upsert_chunk(self, user_id: int, chunk: Chunk) -> None:
        if user_id not in self._data:
            self._data[user_id] = {}
        self._data[user_id][chunk.chunk_id] = chunk

    async def upsert_chunks(self, user_id: int, chunks: list[Chunk]) -> None:
        if user_id not in self._data:
            self._data[user_id] = {}
        for chunk in chunks:
            self._data[user_id][chunk.chunk_id] = chunk

    async def retrieve_by_embedding(
        self, user_id: int, embedding: list[float], topk: int = 3
    ) -> list[Chunk]:
        user_chunks = self._data.get(user_id, {})
        sorted_chunks = sorted(
            user_chunks.values(), key=lambda c: c.created_at, reverse=True
        )
        return sorted_chunks[:topk]

    async def retrieve_by_embedding_batch(
        self, user_id: int, embeddings: list[list[float]], topk: int = 3
    ) -> list[list[Chunk]]:
        raise NotImplementedError("Not implemented in RAM backend")

    async def retrieve_by_type(
        self, user_id: int, chunk_type: str, topk: int = 3
    ) -> list[Chunk]:
        user_chunks = self._data.get(user_id, {})
        filtered = [c for c in user_chunks.values() if c.chunk_type == chunk_type]
        filtered.sort(key=lambda c: c.created_at, reverse=True)
        return filtered[:topk]

    async def retrieve_by_text(
        self, user_id: int, query: str, topk: int = 3
    ) -> list[Chunk]:
        user_chunks = self._data.get(user_id, {})
        filtered = [c for c in user_chunks.values() if query.lower() in c.text.lower()]
        filtered.sort(key=lambda c: c.created_at, reverse=True)
        return filtered[:topk]

    async def merge_old_chunks(self, user_id: int, chunk_type: str, n: int = 5) -> None:
        user_chunks = self._data.get(user_id, {})
        next_type = {"type0": "type1", "type1": "type2"}.get(chunk_type)
        if not next_type:
            return

        candidates = [c for c in user_chunks.values() if c.chunk_type == chunk_type]
        if len(candidates) < n:
            return

        candidates.sort(key=lambda c: c.created_at)
        selected = candidates[:n]

        merged_text = " | ".join([c.text for c in selected])  # mock summary

        new_chunk = Chunk(
            chunk_id=uuid4(),
            user_id=user_id,
            chunk_type=next_type,
            created_at=datetime.now(UTC),
            last_hit=datetime.now(UTC),
            hit_count=0,
            text=merged_text,
            persistent=False,
            summary_of=[c.chunk_id for c in selected],
        )
        for c in selected:
            del user_chunks[c.chunk_id]
        user_chunks[new_chunk.chunk_id] = new_chunk

    async def archive_user(self, user_id: int) -> None:
        if user_id in self._data:
            self._archive[user_id] = self._data[user_id]
            del self._data[user_id]

    async def restore_user(self, user_id: int) -> None:
        if user_id in self._archive:
            self._data[user_id] = self._archive[user_id]
            del self._archive[user_id]

    async def increment_hit(self, user_id: int, chunk_id: UUID) -> None:
        user_chunks = self._data.get(user_id, {})
        chunk = user_chunks.get(chunk_id)
        if chunk is not None:
            chunk.hit_count += 1
            from datetime import datetime

            chunk.last_hit = datetime.now(UTC)

    async def pop_first_n(self, user_id: int, chunk_type: str, n: int) -> list[Chunk]:
        user_chunks = self._data.get(user_id, {})
        filtered = [c for c in user_chunks.values() if c.chunk_type == chunk_type]
        # сортировка по created_at (старые — первые)
        filtered.sort(key=lambda c: c.created_at)
        # выбираем первые n
        selected = filtered[:n]
        # удаляем их из данных
        for chunk in selected:
            del self._data[user_id][chunk.chunk_id]
        return selected

    async def delete_oldest_nonpersistent(self, user_id: int, keep: int) -> None:
        user_chunks = self._data.get(user_id, {})
        nonpersistent = [c for c in user_chunks.values() if not c.persistent]
        # сортировка по created_at (старые — первые)
        nonpersistent.sort(key=lambda c: c.created_at)
        # если их больше чем keep — удаляем лишние
        for chunk in nonpersistent[:-keep]:
            del self._data[user_id][chunk.chunk_id]

    async def delete_chunk(self, user_id: int, chunk_id: UUID) -> None:
        user_chunks = self._data.get(user_id, {})
        user_chunks.pop(chunk_id, None)

    async def delete_chunks(self, user_id: int, chunk_ids: list[UUID]) -> None:
        user_chunks = self._data.get(user_id, {})
        for chunk_id in chunk_ids:
            user_chunks.pop(chunk_id, None)

    async def delete_all(self, user_id: int) -> None:
        self._data.pop(user_id, None)

    def get_all_chunks(self, user_id: int) -> list[Chunk]:
        """Для тестов — все чанки пользователя."""
        return list(self._data.get(user_id, {}).values())

    def get_all_archive(self, user_id: int) -> list[Chunk]:
        """Для тестов — все чанки в архиве."""
        return list(self._archive.get(user_id, {}).values())

    def clear(self):
        """Очистка всех данных для тестов."""
        self._data.clear()
        self._archive.clear()
