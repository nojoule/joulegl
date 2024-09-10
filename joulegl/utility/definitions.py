import os
import sys
from typing import Generator, Tuple, TypeVar

BASE_PATH = os.path.dirname(sys.modules["__main__"].__file__)

# if the environment is set to TESTING, the path will be set to tests/tmp

SCREENSHOT_PATH = (
    os.path.join(BASE_PATH, "screenshots")
    if os.environ.get("TESTING") is None
    else "tests/tmp/screenshots"
)


_T = TypeVar("_T")


def vec4wise(it: _T) -> Generator[Tuple[_T, _T, _T, _T], None, None]:
    it = iter(it)
    while True:
        try:
            yield next(it), next(it), next(it), next(it),
        except StopIteration:
            return
