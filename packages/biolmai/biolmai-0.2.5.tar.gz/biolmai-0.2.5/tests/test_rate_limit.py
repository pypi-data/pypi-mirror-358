import sys
import asyncio
import time
import unittest
if sys.version_info < (3, 8):
    from asynctest import CoroutineMock as AsyncMock
    from unittest.mock import patch
else:
    from unittest.mock import AsyncMock, patch

from biolmai.client import AsyncRateLimiter, BioLMApiClient


class TestAsyncRateLimiter(unittest.IsolatedAsyncioTestCase):
    async def test_rate_limiter_allows_max_calls_per_second(self):
        limiter = AsyncRateLimiter(3, 1.0)  # 3 calls per second
        times = []

        async def task():
            async with limiter.limit():
                times.append(time.monotonic())

        # Run 3 tasks in parallel, should not block
        await asyncio.gather(*(task() for _ in range(3)))
        self.assertLess(times[-1] - times[0], 0.5)

    async def test_rate_limiter_blocks_on_excess_calls(self):
        limiter = AsyncRateLimiter(2, 1.0)  # 2 calls per second
        times = []

        async def task():
            async with limiter.limit():
                times.append(time.monotonic())

        # Run 3 tasks, the 3rd should be delayed by ~1s
        await asyncio.gather(*(task() for _ in range(3)))
        delay = times[2] - times[0]
        self.assertGreaterEqual(delay, 1.0)

    async def test_rate_limiter_minute(self):
        limiter = AsyncRateLimiter(2, 60.0)  # 2 calls per minute
        times = []

        async def task():
            async with limiter.limit():
                times.append(time.monotonic())

        await asyncio.gather(*(task() for _ in range(2)))
        # Both should run immediately
        self.assertLess(times[1] - times[0], 0.5)
        # Third should be delayed by ~60s
        t0 = time.monotonic()
        await task()
        t1 = time.monotonic()
        self.assertGreaterEqual(t1 - t0, 59.0)  # allow some slack

    async def test_rate_limiter_invalid_period(self):
        from biolmai.client import parse_rate_limit
        with self.assertRaises(ValueError):
            parse_rate_limit("5/hour")

class TestSemaphoreConcurrency(unittest.IsolatedAsyncioTestCase):
    async def test_semaphore_limits_concurrency(self):
        sem = asyncio.Semaphore(2)
        running = 0
        max_running = 0

        async def task():
            nonlocal running, max_running
            async with sem:
                running += 1
                max_running = max(max_running, running)
                await asyncio.sleep(0.1)
                running -= 1

        await asyncio.gather(*(task() for _ in range(5)))
        self.assertEqual(max_running, 2)

class TestBioLMApiClientLimitLogic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Patch HttpClient to avoid real HTTP calls
        patcher = patch('biolmai.client.HttpClient')
        self.addCleanup(patcher.stop)
        self.mock_http = patcher.start()
        self.mock_http.return_value.post = AsyncMock()
        self.mock_http.return_value.get = AsyncMock()
        self.mock_http.return_value.close = AsyncMock()

    async def test_limit_with_semaphore_and_rate_limiter(self):
        sem = asyncio.Semaphore(1)
        limiter = AsyncRateLimiter(1, 1.0)
        client = BioLMApiClient("model", semaphore=sem, rate_limit="1/second")
        client._rate_limiter = limiter  # forcibly set for test

        order = []

        async def fake_post(endpoint, payload):
            order.append(time.monotonic())
            await asyncio.sleep(0.01)
            class FakeResp:
                status_code = 200
                headers = {"Content-Type": "application/json"}
                def json(self): return {"ok": True}
            return FakeResp()

        client._http_client.post = fake_post

        async def call():
            return await client._api_call("endpoint", {})

        # Should serialize both by semaphore and by rate limiter
        await asyncio.gather(call(), call())
        self.assertGreaterEqual(order[1] - order[0], 1.0)

    async def test_limit_with_only_semaphore(self):
        sem = asyncio.Semaphore(2)
        client = BioLMApiClient("model", semaphore=sem)
        client._rate_limiter = None

        running = 0
        max_running = 0

        async def fake_post(endpoint, payload):
            nonlocal running, max_running
            running += 1
            max_running = max(max_running, running)
            await asyncio.sleep(0.05)
            running -= 1
            class FakeResp:
                status_code = 200
                headers = {"Content-Type": "application/json"}
                def json(self): return {"ok": True}
            return FakeResp()

        client._http_client.post = fake_post

        await asyncio.gather(*(client._api_call("endpoint", {}) for _ in range(4)))
        self.assertEqual(max_running, 2)

    async def test_limit_with_only_rate_limiter(self):
        limiter = AsyncRateLimiter(1, 1.0)
        client = BioLMApiClient("model", rate_limit="1/second")
        client._rate_limiter = limiter
        client._semaphore = None

        order = []

        async def fake_post(endpoint, payload):
            order.append(time.monotonic())
            class FakeResp:
                status_code = 200
                headers = {"Content-Type": "application/json"}
                def json(self): return {"ok": True}
            return FakeResp()

        client._http_client.post = fake_post

        await asyncio.gather(client._api_call("endpoint", {}), client._api_call("endpoint", {}))
        self.assertGreaterEqual(order[1] - order[0], 1.0)

    async def test_limit_with_neither(self):
        client = BioLMApiClient("model")
        client._rate_limiter = None
        client._semaphore = None

        called = []

        async def fake_post(endpoint, payload):
            called.append(1)
            class FakeResp:
                status_code = 200
                headers = {"Content-Type": "application/json"}
                def json(self): return {"ok": True}
            return FakeResp()

        client._http_client.post = fake_post

        await asyncio.gather(*(client._api_call("endpoint", {}) for _ in range(5)))
        self.assertEqual(len(called), 5)

if __name__ == "__main__":
    unittest.main()
