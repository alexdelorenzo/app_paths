from __future__ import annotations
from enum import auto

from strenum import StrEnum

from .io import Paths


class AppPath(StrEnum):
  site_config_path: str = auto()
  site_data_path: str = auto()

  user_cache_path: str = auto()
  user_config_path: str = auto()
  user_data_path: str = auto()
  user_log_path: str = auto()
  user_state_path: str = auto()

  @staticmethod
  def from_name(name: str) -> AppPath:
    return get_app_path(name)


PathNames = dict[AppPath, Paths]


def get_app_path(name: str) -> AppPath:
  return getattr(AppPath, name)
