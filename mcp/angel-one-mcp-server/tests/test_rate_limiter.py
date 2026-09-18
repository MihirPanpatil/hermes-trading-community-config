import asyncio
import time

from angel_one_mcp.rate_limiter import AsyncRequestGate, TTLCache


def test_gate_spaces_requests():
    async def run():
        gate = AsyncRequestGate(min_interval=0.03)
        times = []
        for _ in range(3):
            async with gate:
                times.append(time.monotonic())
        return times

    times = asyncio.run(run())
    assert times[1] - times[0] >= 0.025
    assert times[2] - times[1] >= 0.025


def test_cache_expires_entries():
    cache = TTLCache()
    cache.set("x", {"value": 1}, ttl=0.02)
    assert cache.get("x") == {"value": 1}
    time.sleep(0.03)
    assert cache.get("x") is None


def test_gate_serializes_concurrent_requests():
    async def run():
        gate = AsyncRequestGate(min_interval=0.02)
        active = 0
        peak = 0

        async def one():
            nonlocal active, peak
            async with gate:
                active += 1
                peak = max(peak, active)
                await asyncio.sleep(0.01)
                active -= 1

        await asyncio.gather(one(), one(), one())
        return peak

    assert asyncio.run(run()) == 1
