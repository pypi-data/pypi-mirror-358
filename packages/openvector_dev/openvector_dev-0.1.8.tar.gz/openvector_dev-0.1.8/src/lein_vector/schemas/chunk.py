from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    chunk_id: UUID
    user_id: int
    bot: str
    chunk_type: str  # "type0" | "type1" | "fact"
    created_at: datetime
    last_hit: datetime
    hit_count: int = 0
    text: str
    persistent: bool = False

    summary_of: list[UUID] | None = None  # для type1
    source_chunk_id: UUID | None = None  # для fact
    extra: dict | None = Field(default_factory=dict)

    def to_payload(self) -> ChunkPayload:
        return ChunkPayload(**self.model_dump())


class ChunkPayload(BaseModel):
    chunk_id: UUID
    user_id: int
    chunk_type: str
    created_at: datetime
    text: str
    persistent: bool = False
    summary_of: list[UUID] | None = None
    source_chunk_id: UUID | None = None
    extra: dict | None = Field(default_factory=dict)

    def to_chunk(self, last_hit: datetime = None, hit_count: int = 0) -> Chunk:
        return Chunk(
            **self.model_dump(),
            last_hit=last_hit or datetime.now(UTC),
            hit_count=hit_count,
        )
