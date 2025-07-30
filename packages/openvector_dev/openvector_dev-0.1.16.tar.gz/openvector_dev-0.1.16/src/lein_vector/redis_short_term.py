import json
import logging
from datetime import UTC, datetime

import redis.asyncio as aioredis


class RedisShortTermMemory:
    """
    Хранит окно последних сообщений пользователя в Redis-списке.
    Формат элемента — JSON-строка с полями role / text / ts / extra…
    Ключ для пользователя:  {codename}:{user_id}:short_term
    """

    def __init__(self, redis: aioredis.Redis, maxlen: int = 20):
        self.r = redis
        self.maxlen = maxlen

    @staticmethod
    def _key(user_id: int, bot: str) -> str:
        return f"{bot}:{user_id}:short_term"

    @staticmethod
    def _dump(msg: dict) -> str:
        # datetime => iso
        if isinstance(msg.get("ts"), datetime):
            msg = {**msg, "ts": msg["ts"].isoformat()}
        return json.dumps(msg, ensure_ascii=False)

    async def add(
        self,
        user_id: int,
        bot: str,
        role: str,
        text: str,
        ts: datetime | None = None,
        **extra,
    ) -> None:
        if ts is None:
            ts = datetime.now(UTC)

        msg = self._dump({"role": role, "text": text, "ts": ts, **extra})
        key = self._key(user_id, bot=bot)

        pipe = self.r.pipeline()
        await pipe.rpush(key, msg)
        await pipe.ltrim(key, -self.maxlen, -1)
        await pipe.execute()

    @staticmethod
    def _load(raw: str | bytes) -> dict:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        d = json.loads(raw)
        if "ts" in d:
            try:
                d["ts"] = datetime.fromisoformat(d["ts"])
            except ValueError:
                logging.error("Invalid timestamp: %s", d["ts"])
        return d

    async def window(self, user_id: int, bot: str, n: int | None = None) -> list[dict]:
        n = n or self.maxlen
        raw = await self.r.lrange(self._key(user_id, bot=bot), -n, -1)
        return [self._load(r) for r in raw]

    async def clear(self, bot: str, user_id: int) -> None:
        await self.r.delete(self._key(user_id, bot=bot))

    async def load(self, user_id: int, bot: str, history: list[dict]) -> None:
        history = history[-self.maxlen :]
        if not history:
            await self.clear(user_id)
            return
        key = self._key(user_id, bot=bot)
        pipe = self.r.pipeline()
        await pipe.delete(key)
        await pipe.rpush(key, *[self._dump(m) for m in history])
        await pipe.execute()

    async def to_list(self, user_id: int, bot: str) -> list[dict]:
        raw = await self.r.lrange(self._key(user_id, bot=bot), 0, -1)
        return [self._load(r) for r in raw]

    async def chunk_for_vector(
        self, user_id: int, bot: str, chunk_size: int = 6
    ) -> list[dict] | None:
        raw_len = await self.r.llen(self._key(user_id, bot=bot))
        if raw_len < chunk_size:
            return None
        raw = await self.r.lrange(self._key(user_id, bot=bot), -chunk_size, -1)
        return [self._load(r) for r in raw]
