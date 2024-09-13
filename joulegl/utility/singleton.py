from __future__ import annotations

from typing import Any, Type, TypeVar

_T = TypeVar("_T")
_TS = TypeVar("_TS", "Singleton", _T)


class Singleton(type):
    _instances = {}

    def __call__(cls: _TS, *args, **kwargs) -> _T:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
