import asyncio

from google import genai
from google.genai import types

from lein_vector.bases.embeding_provider_abc import EmbeddingProviderABC


class EmbeddingProviderGemini(EmbeddingProviderABC):
    def __init__(self, api_key: str, model_name: str = "models/embedding-001"):

        self.client = genai.Client(api_key=api_key)
        self.model = model_name

    def _genai_embed(self, text: str | list) -> types.EmbedContentResponse:
        return self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
        )

    async def get_embedding(self, text: str) -> list[float]:
        # В Gemini SDK обычно нет async, значит — обёртка через run_in_executor:
        import asyncio

        if not isinstance(text, str):
            return
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(None, lambda: self._genai_embed(text))
        return embedding.embeddings[0].values

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        import asyncio

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, lambda: self._genai_embed(texts))
        # Вернуть список эмбеддингов
        return [e.values for e in result.embeddings]


async def main():
    embeding = EmbeddingProviderGemini(
        api_key="AIzaSyDK_pkj25Cbb0iUujYm6N4K1k7xzeD_kss"
    )
    print(str(await embeding.get_embedding("test"))[:50] + "... TRIMMED]\n")
    res = await embeding.get_embeddings(["test", "test2"])
    print(len(res))
    for e in res:
        print(str(e)[:50] + "... TRIMMED]")


if __name__ == "__main__":
    asyncio.run(main())
