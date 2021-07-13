from __future__ import annotations
from typing import Union, Optional, Callable, Awaitable, Any, \
  Coroutine
from pathlib import Path
from functools import lru_cache, wraps
from inspect import iscoroutinefunction, isawaitable
from asyncio import gather, run, Task, Future

from aiopath import AsyncPath
from asyncstdlib import lru_cache as lru_async


MAX_SIZE: Optional[int] = None
MKDIR_ARGS: dict[str, bool] = dict(parents=True, exist_ok=True)


Paths = Union[Path, AsyncPath]
PathsReturnTypes = Union[Paths, Awaitable[Paths]]
ReturnsPaths = Callable[..., PathsReturnTypes]


@lru_cache(MAX_SIZE)
def make_dir(path: Path):
  if isinstance(path, AsyncPath):
    path = Path(path)

  path.mkdir(**MKDIR_ARGS)


@lru_async(MAX_SIZE)
async def make_dir_async(path: Paths):
  if not isinstance(path, AsyncPath):
    path = AsyncPath(path)

  await path.mkdir(**MKDIR_ARGS)


async def run_coros_async(*coros: Coroutine) -> list:
  return await gather(*coros)


def run_coros(*coros: Coroutine) -> list:
  coro = run_coros_async(*coros)
  return run(coro)


def create_path(func: ReturnsPaths) -> ReturnsPaths:
  if iscoroutinefunction(func):
    @wraps(func)
    async def new_func(*args, **kwargs) -> AsyncPath:
      path = await func(*args, **kwargs)
      await make_dir_async(path)

      return path

  else:
    @wraps(func)
    def new_func(*args, **kwargs) -> Path:
      path = func(*args, **kwargs)
      make_dir(path)

      return path

  return new_func
