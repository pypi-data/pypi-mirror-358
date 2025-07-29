import asyncio
import sys
from typing import Any

import pytest

from conrun import Runner


# ───────────────────────── helpers ──────────────────────────
async def aio_echo(x: str) -> str:
    await asyncio.sleep(0.01)
    return x.upper()


def sync_echo(x: str) -> str:
    return x.upper()


# ───────────────────────── sync API (run) ───────────────────
def test_run_async_mode_sync_api():
    runner = Runner(mode="async", max_workers=3)
    res = runner.run(aio_echo, ["a", "b", "c"])
    assert res == ["A", "B", "C"]


def test_run_thread_mode_sync_api():
    runner = Runner(mode="thread", max_workers=3)
    res = runner.run(sync_echo, ["a", "b", "c"])
    assert res == ["A", "B", "C"]


@pytest.mark.skipif(sys.platform == "darwin" and sys.version_info >= (3, 12),
                    reason="sporadic fork issues on macOS 3.12+")
def test_run_process_mode_sync_api():
    runner = Runner(mode="process", max_workers=2)
    res = runner.run(sync_echo, ["a", "b"])
    assert res == ["A", "B"]


# ───────────────────────── async API (arun) ─────────────────
@pytest.mark.asyncio
async def test_arun_async_mode():
    runner = Runner(mode="async", max_workers=2)
    res = await runner.arun(aio_echo, ["x", "y"])
    assert res == ["X", "Y"]


@pytest.mark.asyncio
async def test_arun_thread_mode():
    runner = Runner(mode="thread", max_workers=2)
    res = await runner.arun(sync_echo, ["x", "y"])
    assert res == ["X", "Y"]


@pytest.mark.asyncio
async def test_arun_return_exceptions():
    async def boom(_: Any) -> None:  # noqa: D401
        raise ValueError("boom")

    runner = Runner(mode="async", max_workers=1)
    res = await runner.arun(boom, ["ignored"], return_exceptions=True)
    assert isinstance(res[0], ValueError)


# ───────────────────────── depth / executor shutdown ─────────
@pytest.mark.asyncio
async def test_nested_calls_single_shutdown(monkeypatch):
    """Executor is shut down exactly once even with nested calls."""
    runner = Runner(mode="thread", max_workers=4)

    counter = {"calls": 0}
    original_shutdown = runner._executor.shutdown

    def spy_shutdown(*args, **kwargs):
        counter["calls"] += 1
        return original_shutdown(*args, **kwargs)

    monkeypatch.setattr(runner._executor, "shutdown", spy_shutdown)

    def inner_sync(x: str) -> str:
        return runner.run(sync_echo, [x])[0]

    outer_result = await runner.arun(inner_sync, ["n1", "n2"])

    assert outer_result == ["N1", "N2"]
    assert counter["calls"] == 1


# ───────────────────────── invalid parameters ───────────────
def test_invalid_max_workers():
    with pytest.raises(ValueError):
        Runner(mode="async", max_workers=0)
