from typing import Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import MatchText
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from lein_vector.schemas.chunk import ChunkPayload


class QdrantAdapter:
    def __init__(
        self,
        host: str,
        port: int,
        collection: str = "persona_mem",
        vector_size: int = 768,
    ):
        self.collection = collection
        self.client = AsyncQdrantClient(host=host, port=port)
        self.vector_size = vector_size

    async def init_collection(self):
        exists = await self.client.collection_exists(self.collection)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

    async def upsert(
        self, point_id: UUID, embedding: list[float], payload: ChunkPayload
    ) -> None:
        await self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=str(point_id), vector=embedding, payload=payload.model_dump()
                )
            ],
        )

    async def upsert_batch(self, points: list[dict[str, Any]]) -> None:
        structs = [
            PointStruct(
                id=str(point["point_id"]),
                vector=point["embedding"],
                payload=point["payload"].dict(),
            )
            for point in points
        ]
        await self.client.upsert(collection_name=self.collection, points=structs)

    async def search(
        self,
        embedding: list[float],
        filter_: dict[str, Any],
        topk: int,
        score_threshold: float | None = None,
    ) -> list[ChunkPayload]:
        # Пример фильтра {"user_id": 123, "chunk_type": "type1", "created_at_gt": "2024-01-01T00:00:00"}
        conditions = []
        for k, v in filter_.items():
            if k.endswith("_gt"):
                field = k[:-3]
                conditions.append(FieldCondition(key=field, range=Range(gt=v)))
            elif k.endswith("_lt"):
                field = k[:-3]
                conditions.append(FieldCondition(key=field, range=Range(lt=v)))
            elif isinstance(v, str):
                conditions.append(FieldCondition(key=k, match=MatchText(text=v)))
            else:
                conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
        q_filter = Filter(must=conditions)
        result = await self.client.query_points(
            collection_name=self.collection,
            query=embedding,
            query_filter=q_filter,
            limit=topk,
            score_threshold=score_threshold,
        )
        points = result.points
        if len(points) > 0:
            for chunk in points:
                print(chunk.score)
        return [ChunkPayload(**point.payload) for point in points]

    async def delete(self, point_id: UUID) -> None:
        await self.client.delete(
            collection_name=self.collection, points_selector=[str(point_id)]
        )

    async def delete_batch(self, point_ids: list[UUID]) -> None:
        await self.client.delete(
            collection_name=self.collection,
            points_selector=[str(pid) for pid in point_ids],
        )

    async def delete_collection(self) -> None:
        await self.client.delete_collection(collection_name=self.collection)

    async def get_all_chunks(self, user_id: int) -> list[ChunkPayload]:
        q_filter = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
        scroll = await self.client.scroll(
            collection_name=self.collection,
            scroll_filter=q_filter,
            limit=2048,
        )
        return [ChunkPayload(**p.payload) for p in scroll[0]]
