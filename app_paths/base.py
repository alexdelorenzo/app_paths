from __future__ import annotations
from typing import Union, Optional, Iterable, Callable, \
  Any
from abc import ABC, abstractstaticmethod
from functools import partial
from pathlib import Path
from enum import auto
from dataclasses import dataclass, field, asdict
from asyncio import gather, run, Task

from unpackable import Unpackable
from aiopath import AsyncPath
from appdirs import AppDirs
from strenum import StrEnum

from .io import make_dir_async, create_path, run_coros, \
  Paths


PathNames = dict[AppPath, Paths]


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
  ):
    pass

  @property
  def as_dict(self) -> PathNames:
    name_paths = asdict(self)

    return {
      AppPath.from_name(name): path
      for name, path in name_paths.items()
    }

  @property
  def site_paths(self) -> PathNames:
    return {
      name: path
      for name, path in self.as_dict.items()
      if name.startswith('site')
    }

  @property
  def user_paths(self) -> PathNames:
    return {
      name: path
      for name, path in self.as_dict.items()
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
  ):
    paths = \
      get_async_paths(appname, appauthor, version, roaming, multipath)

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
  ):
    paths = \
      get_paths(appname, appauthor, version, roaming, multipath)

    coros = []

    if create_user:
      coro = paths.create_user_paths()
      coros.append(coro)

    if create_site:
      coro = paths.create_site_paths()
      coros.append(coro)

    if coros:
      run_coros(*coros)

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


get_async_paths: Callable[..., AppPathsAsync] = \
  partial(get_paths, is_async=True)


class AppPath(StrEnum):
  site_config_path: str = auto()
  site_data_path: str = auto()

  user_cache_path: str = auto()
  user_config_path: str = auto()
  user_data_path: str = auto()
  user_log_path: str = auto()
  user_state_path: str = auto()

  @classmethod
  def from_name(cls: type, name: str) -> AppPath:
    return get_app_path(name)


def get_app_path(name: str) -> AppPath:
  return getattr(AppPath, name)
