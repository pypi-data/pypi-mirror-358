# Persona-Memory Subsystem

## Назначение:
Модуль памяти для диалогового ИИ-агента.

Short-term: последние сообщения (RAM, deque).

Long-term: Qdrant + архив (долговременные факты и истории).

## Архитектура:
ShortTermMemory — хранит последние сообщения.

QdrantAdapter — async-слой для поиска/хранения чанков в Qdrant.

MemoryManagerQdrant — бизнес-логика.

EmbeddingProviderSentenceTransformer / Gemini — эмбеддинги.

MemoryService (фасад) — единая точка для верхнего слоя.

Chunk / ChunkPayload — pydantic-модели для хранения.

## Пример рабочего цикла:
```
mem = MemoryService(short_term, memory_manager)
mem.add_short("user", user_msg)
emb = await embedder.get_embedding(user_msg)
long_memories = await mem.get_long(user_id, emb, k=3)
short_ctx = mem.get_short(10)
mem.add_short("gf", answer)
await mem.save_long(user_id, Chunk(
    chunk_id=uuid4(), user_id=user_id, chunk_type="type0",
    created_at=datetime.utcnow(), last_hit=datetime.utcnow(),
    hit_count=0, text=answer, persistent=False
))
```

## Установка и тесты:
```
poetry add ./vector-memory

docker run -d --name qdrant -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
  
pytest
```

## Конфигурация:
```
QDRANT_HOST, QDRANT_PORT
QDRANT_COLLECTION
VECTOR_SIZE (совпадает с embedding-моделью)
GEMINI_API_KEY (Gemini Embedding-004)
```

## Перед релизом:
- Все тесты проходят (pytest)
- Размеры векторов и коллекции совпадают
- Архивирование/restore, merge, фильтры работают
- Нет deprecated-методов в adapter

## Roadmap:
- Redis-кеш для hit_count
- Курсорный scroll для больших архивов
- gRPC/gateway-адаптер

## Test-Coverage
```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src\bases\memory_manager_abc.py      20      1    95%
src\memory_manager_qdrant.py         54     11    80%
src\memory_manager_ram.py            95     32    66%
src\qdrant_adapter.py                46      8    83%
src\schemas\chunk.py                 31      1    97%
src\short_term.py                    26      1    96%
-----------------------------------------------------
TOTAL                               272     54    80%
```

