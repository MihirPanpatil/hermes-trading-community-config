"""Small in-process controls for the single Angel One MCP session."""

import asyncio
import time
from collections.abc import Callable
from typing import Any


class AsyncRequestGate:
    """Serialize provider calls and maintain a minimum interval between starts."""

    def __init__(self, min_interval: float = 1.5) -> None:
        self.min_interval = max(0.0, min_interval)
        self._lock = asyncio.Lock()
        self._last_started = 0.0

    async def __aenter__(self) -> "AsyncRequestGate":
        await self._lock.acquire()
        delay = self.min_interval - (time.monotonic() - self._last_started)
        if delay > 0:
            await asyncio.sleep(delay)
        self._last_started = time.monotonic()
        return self

    async def __aexit__(self, *_: Any) -> None:
        self._lock.release()


class TTLCache:
    """Minimal process-local TTL cache; no credentials or responses are persisted."""

    def __init__(self) -> None:
        self._values: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        value = self._values.get(key)
        if value is None:
            return None
        expires, result = value
        if time.monotonic() >= expires:
            self._values.pop(key, None)
            return None
        return result

    def set(self, key: str, result: Any, ttl: float) -> None:
        self._values[key] = (time.monotonic() + max(0.0, ttl), result)


async def gated_call(
    gate: AsyncRequestGate,
    func: Callable[..., Any],
    *args: Any,
    retries: int = 0,
    **kwargs: Any,
) -> Any:
    """Run a blocking SmartAPI SDK call under the shared request gate."""
    for attempt in range(retries + 1):
        try:
            async with gate:
                return await asyncio.to_thread(func, *args, **kwargs)
        except Exception:
            if attempt >= retries:
                raise
            await asyncio.sleep(min(60.0, 5.0 * (2**attempt)))
