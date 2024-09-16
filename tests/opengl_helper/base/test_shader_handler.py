import os
from pathlib import Path
from typing import Tuple

import pytest

from joulegl.opengl_helper.base.shader_handler import BaseShaderHandler
from joulegl.utility.definitions import SHADER_PATH


@pytest.mark.parametrize(
    "paths",
    [
        (None, SHADER_PATH),
        (SHADER_PATH, SHADER_PATH),
        (
            os.path.join(
                Path(Path(SHADER_PATH).parent.absolute()).parent.absolute(),
                "non_existant",
            ),
            os.path.join(
                Path(Path(SHADER_PATH).parent.absolute()).parent.absolute(),
                "non_existant",
            ),
        ),
        (
            str(
                os.path.join(Path(SHADER_PATH).parent.absolute(), "shader_not_existing")
            ),
            str(Path(SHADER_PATH).absolute()),
        ),
    ],
)
def test_shader_handler_path(paths: Tuple[str | None, str]) -> None:
    input_path, expected_path = paths
    if input_path is None:
        base_shader_handler = BaseShaderHandler()
    else:
        base_shader_handler = BaseShaderHandler(input_path)

    assert base_shader_handler.shader_dir == expected_path
