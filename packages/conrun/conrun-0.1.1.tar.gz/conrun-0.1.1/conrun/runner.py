from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    List,
    Literal,
    Mapping,
    TypeVar,
)

T = TypeVar("T")


class Runner:

    def __init__(
        self,
        *,
        mode: Literal["async", "thread", "process"],
        max_workers: int,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")

        self.mode = mode
        self.max_workers = max_workers
        self._sem = asyncio.BoundedSemaphore(max_workers)
        self._depth = 0

        if mode == "thread":
            self._executor: ThreadPoolExecutor | ProcessPoolExecutor | None = (
                ThreadPoolExecutor(max_workers)
            )
        elif mode == "process":
            self._executor = ProcessPoolExecutor(max_workers)
        else:  # pure asyncio
            self._executor = None

    def run(
        self,
        task: Callable[..., Awaitable[T]] | Callable[..., T],
        arguments: Iterable[Any],
        return_exceptions: bool = False,
    ) -> List[T]:
        return asyncio.run(
            self.arun(task, arguments, return_exceptions=return_exceptions)
        )
    
    async def arun(
        self,
        task: Callable[..., Awaitable[T]] | Callable[..., T],
        arguments: Iterable[Any],
        return_exceptions: bool = False,
    ) -> List[T]:
        loop = asyncio.get_running_loop()

        self._depth += 1
        try:
            queue: asyncio.Queue[tuple[int, Any]] = asyncio.Queue()
            for idx, arg in enumerate(arguments):
                queue.put_nowait((idx, arg))

            results: List[Any] = [None] * queue.qsize()

            
            async def invoke(arg: Any) -> T:
                if isinstance(arg, Mapping):
                    positional, keyword = (), arg
                elif isinstance(arg, (list, tuple)):
                    positional, keyword = arg, {}
                else:
                    positional, keyword = (arg,), {}

                if self.mode == "async":
                    res = task(*positional, **keyword)  # type: ignore[arg-type]
                    return await res if asyncio.iscoroutine(res) else res

                # thread / process
                return await loop.run_in_executor(      # type: ignore[arg-type]
                    self._executor, task, *positional, **keyword
                )
            
            async def worker() -> None:
                while True:
                    try:
                        idx, arg = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                    try:
                        async with self._sem:
                            results[idx] = await invoke(arg)
                    except Exception as exc:  # noqa: BLE001
                        if return_exceptions:
                            results[idx] = exc
                        else:
                            while not queue.empty():
                                queue.get_nowait()
                                queue.task_done()
                            raise
                    finally:
                        queue.task_done()

            n_workers = min(self.max_workers, len(results))
            tasks = [asyncio.create_task(worker()) for _ in range(n_workers)]
            await queue.join()
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            return results  # type: ignore[return-value]

        finally:
            # close executor only once
            self._depth -= 1
            if self._depth == 0 and self._executor is not None:
                self._executor.shutdown(wait=True)
    
    async def aclose(self) -> None:
        if self._executor and not self._executor._shutdown:
            self._executor.shutdown(wait=True)
