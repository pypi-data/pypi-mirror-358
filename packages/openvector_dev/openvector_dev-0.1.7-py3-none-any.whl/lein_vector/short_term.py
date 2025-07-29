from collections import deque
from datetime import datetime


class ShortTermMemory:
    def __init__(self, maxlen: int = 10):
        self._buffer: deque = deque(maxlen=maxlen)

    def add(
        self,
        codename: str,
        user_id: int,
        role: str,
        text: str,
        ts: datetime | None = None,
        **extra
    ) -> None:
        """Добавить сообщение в память (роль, текст, ts - время, по умолчанию now)."""
        if ts is None:
            ts = datetime.now()
        self._buffer.append({"role": role, "text": text, "ts": ts, **extra})

    def window(self, n: int | None = None) -> list[dict]:
        """Получить последние n сообщений (по умолчанию все)."""
        if n is None or n > len(self._buffer):
            return list(self._buffer)
        return list(self._buffer)[-n:]

    def clear(self) -> None:
        """Очистить память."""
        self._buffer.clear()

    def load(self, history: list[dict]) -> None:
        """Инициализировать память списком сообщений."""
        self._buffer.clear()
        for msg in history[-self._buffer.maxlen :]:
            self._buffer.append(msg)

    def to_list(self) -> list[dict]:
        """Выгрузить всю память как список."""
        return list(self._buffer)

    def chunk_for_vector(self, chunk_size: int = 6) -> list[dict] | None:
        """Сформировать чанк для векторной БД — N последних сообщений по хронологии."""
        if len(self._buffer) < chunk_size:
            return None
        # Забираем chunk_size старейших, но не очищаем (внешний код решает)
        return list(self._buffer)[-chunk_size:]
