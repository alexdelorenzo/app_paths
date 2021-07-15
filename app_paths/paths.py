from __future__ import annotations
from typing import Union, Optional, Iterable, Callable, \
  Any
from abc import ABC, abstractstaticmethod
from functools import partial
from pathlib import Path
from dataclasses import dataclass, field, asdict
from asyncio import gather, run, Task

from anyio.to_thread import run_sync
from unpackable import Unpackable
from aiopath import AsyncPath
from appdirs import AppDirs

from .io import make_dir_async, create_path, run_coros, \
  Paths
from .base import AppPath


@dataclass
class AppPathsBase(ABC, Unpackable):
  site_config_path: Paths
  site_data_path: Paths

  user_cache_path: Paths
  user_config_path: Paths
  user_data_path: Paths
  user_log_path: Paths
  user_state_path: Paths

  @abstractstaticmethod
  def get_paths(
    appname: Optional[str] = None,
    appauthor: Optional[str] = None,
    version: Optional[str] = None,
    roaming: bool = False,
    multipath: bool = False,
    create_site: bool = False,
    create_user: bool = False,
  ) -> AppPathsBase:
    pass

  @property
  def all_paths(self) -> PathNames:
    name_paths = asdict(self)

    return {
      AppPath.from_name(name): path
      for name, path in name_paths.items()
    }

  @property
  def site_paths(self) -> PathNames:
    return {
      name: path
      for name, path in self.all_paths.items()
      if name.startswith('site')
    }

  @property
  def user_paths(self) -> PathNames:
    return {
      name: path
      for name, path in self.all_paths.items()
      if name.startswith('user')
    }

  async def create_site_paths(self):
    config, data, *_ = self
    paths = config, data

    coros = map(make_dir_async, paths)
    await gather(*coros)

  async def create_user_paths(self):
    _, _, *paths = self

    coros = map(make_dir_async, paths)
    await gather(*coros)

  async def create_all(self):
    coros = (
      self.create_site_paths(),
      self.create_user_paths(),
    )

    await gather(*coros)


@dataclass
class AsyncAppPaths(AppPathsBase):
  site_config_path: AsyncPath
  site_data_path: AsyncPath

  user_cache_path: AsyncPath
  user_config_path: AsyncPath
  user_data_path: AsyncPath
  user_log_path: AsyncPath
  user_state_path: AsyncPath

  @staticmethod
  async def get_paths(
    appname: Optional[str] = None,
    appauthor: Optional[str] = None,
    version: Optional[str] = None,
    roaming: bool = False,
    multipath: bool = False,
    create_site: bool = False,
    create_user: bool = False,
  ) -> AsyncAppPaths:
    paths = await get_async_paths(
      appname, appauthor, version, roaming, multipath
    )

    coros = []

    if create_user:
      coro = paths.create_user_paths()
      coros.append(coro)

    if create_site:
      coro = paths.create_site_paths()
      coros.append(coro)

    if coros:
      await gather(*coros)

    return paths

  @property
  @create_path
  async def site_config(self) -> AsyncPath:
    return self.site_config_path

  @property
  @create_path
  async def site_data(self) -> AsyncPath:
    return self.site_data_path

  @property
  @create_path
  async def user_cache(self) -> AsyncPath:
    return self.user_cache_path

  @property
  @create_path
  async def user_config(self) -> AsyncPath:
    return self.user_config_path

  @property
  @create_path
  async def user_data(self) -> AsyncPath:
    return self.user_data_path

  @property
  @create_path
  async def user_log(self) -> AsyncPath:
    return self.user_log_path

  @property
  @create_path
  async def user_state(self) -> AsyncPath:
    return self.user_state_path


@dataclass
class AppPaths(AppPathsBase):
  site_config_path: Path
  site_data_path: Path

  user_cache_path: Path
  user_config_path: Path
  user_data_path: Path
  user_log_path: Path
  user_state_path: Path

  @staticmethod
  def get_paths(
    appname: Optional[str] = None,
    appauthor: Optional[str] = None,
    version: Optional[str] = None,
    roaming: bool = False,
    multipath: bool = False,
    create_site: bool = False,
    create_user: bool = False,
  ) -> AppPaths:
    paths = \
      get_paths(appname, appauthor, version, roaming, multipath)

    if create_user:
      paths.create_user_paths()

    if create_site:
      paths.create_site_paths()

    return paths

  def create_site_paths(self):
    coro = super().create_site_paths()
    run(coro)

  def create_user_paths(self):
    coro = super().create_user_paths()
    run(coro)

  def create_all(self):
    coro = super().create_all()
    run(coro)

  @property
  @create_path
  def site_config(self) -> Path:
    return self.site_config_path

  @property
  @create_path
  def site_data(self) -> Path:
    return self.site_data_path

  @property
  @create_path
  def user_cache(self) -> Path:
    return self.user_cache_path

  @property
  @create_path
  def user_config(self) -> Path:
    return self.user_config_path

  @property
  @create_path
  def user_data(self) -> Path:
    return self.user_data_path

  @property
  @create_path
  def user_log(self) -> Path:
    return self.user_log_path

  @property
  @create_path
  def user_state(self) -> Path:
    return self.user_state_path


def get_paths(
  appname: Optional[str] = None,
  appauthor: Optional[str] = None,
  version: Optional[str] = None,
  roaming: bool = False,
  multipath: bool = False,
  is_async: bool = False,
) -> Union[AppPaths, AppPathsAsync]:
  dirs = AppDirs(
    appname,
    appauthor,
    version,
    roaming,
    multipath
  )

  dir_names: tuple[str] = (
    dirs.site_config_dir,
    dirs.site_data_dir,
    dirs.user_cache_dir,
    dirs.user_config_dir,
    dirs.user_data_dir,
    dirs.user_log_dir,
    dirs.user_state_dir,
  )

  if is_async:
    paths = map(AsyncPath, dir_names)
    return AsyncAppPaths(*paths)

  paths = map(Path, dir_names)
  return AppPaths(*paths)


async def get_async_paths(
  appname: Optional[str] = None,
  appauthor: Optional[str] = None,
  version: Optional[str] = None,
  roaming: bool = False,
  multipath: bool = False,
):
  func = partial(
    get_paths,
    appname,
    appauthor,
    version,
    roaming,
    multipath,
    is_async=True,
  )

  return await to_thread(func)
