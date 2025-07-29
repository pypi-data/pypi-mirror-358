from abc import ABC, abstractmethod


class EmbeddingProviderABC(ABC):
    @abstractmethod
    async def get_embedding(self, text: str) -> list[float]: ...

    @abstractmethod
    async def get_embeddings(self, texts: list[str]) -> list[list[float]]: ...
