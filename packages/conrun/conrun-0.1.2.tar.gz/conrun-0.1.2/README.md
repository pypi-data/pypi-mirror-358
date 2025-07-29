# conrun

[![ci](https://github.com/DmitriiKhudiakov/conrun/actions/workflows/ci.yml/badge.svg?label=tests)](https://github.com/DmitriiKhudiakov/conrun/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/conrun.svg?label=pypi%20package)](https://pypi.org/project/conrun/)
[![Python](https://img.shields.io/pypi/pyversions/conrun.svg?label=python)](https://pypi.org/project/conrun/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Simple concurrent runner for **async tasks**, **threads** and **processes** – one API, one object.

## ⚠️ Work-in-progress

> `conrun` is under active development. Until `v1.0` the public API **may change without notice**.
Feel free to experiment, but pin the exact version in production.

## Features

* One-liner concurrency – run any coroutine, function, or CPU-bound task concurrently with a single call.
* Three modes
  • `async`   → native `asyncio` concurrency
  • `thread`  → `ThreadPoolExecutor` under the hood
  • `process` → `ProcessPoolExecutor` for CPU-bound work
* Safe nesting – a single `Runner` can be reused recursively; the executor shuts down exactly once.
* Back-pressure – `max_workers` + semaphore keep concurrency under control.
* Sync *and* async entry points – call from “normal” code (`run`) or inside an event loop (`arun`).

Supported Python versions: **3.10 · 3.11 · 3.12 · 3.13**

## Installation

```shell
pip install conrun
```

## Quick start

```python
import asyncio
from conrun import Runner


async def my_function(text: str) -> str:
    await asyncio.sleep(1)
    return text.upper()


async def main():
    result = await Runner(mode="async", max_workers=3).arun(
        my_function,
        ["a", "b", "c"],
    )
    print(result)  # ['A', 'B', 'C']


if __name__ == "__main__":
    asyncio.run(main())
```


## License

MIT – см. файл `LICENSE`.
