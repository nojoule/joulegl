import os
import sys
from typing import Generator, Tuple, TypeVar

BASE_PATH = os.path.dirname(sys.modules["__main__"].__file__)
SCREENSHOT_PATH = os.path.join(os.getcwd(), "storage", "screenshots")

_T = TypeVar("_T")


def vec4wise(it: _T) -> Generator[Tuple[_T, _T, _T, _T], None, None]:
    it = iter(it)
    while True:
        try:
            yield next(it), next(it), next(it), next(it),
        except StopIteration:
            return
