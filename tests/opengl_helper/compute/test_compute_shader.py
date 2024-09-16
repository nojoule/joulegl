from typing import Generator

import numpy as np
import pytest
from OpenGL.GL import *

from joulegl.opengl_helper.compute.shader import ComputeShaderSetting
from joulegl.opengl_helper.compute.shader_handler import ComputeShaderHandler
from joulegl.opengl_helper.texture import Texture
from joulegl.utility.glcontext import GLContext


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


def test_wrong_shader_file_count() -> None:
    with pytest.raises(Exception) as e:
        ComputeShaderSetting("id", ["comp", "extra"])
    assert (
        e.value.args[0] == "Can't handle number of shaders for a program (must be 1)."
    )


def test_set_textures(gl_context: GLContext) -> None:
    texture = Texture(100, 100)
    texture.setup(np.array([255] * 100 * 100 * 4, dtype=np.uint8), 0)

    shader_settings = [
        ComputeShaderSetting(
            "add",
            [
                "add.comp",
            ],
        ),
    ]
    shader_handler = ComputeShaderHandler()
    shader = shader_handler.create(shader_settings[0])
    shader.set_textures([(texture, "read_only", 0)])

    texture, flag, position = shader.textures[0]
    assert flag == "read_only"
    assert position == 0
    assert texture.width == 100
    assert texture.height == 100

    shader.use()
    shader.compute(1)
    assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture.ogl_handle


def test_compute_workgroup_max(gl_context: GLContext) -> None:
    shader_settings = [
        ComputeShaderSetting(
            "add",
            [
                "add.comp",
            ],
        ),
    ]
    shader_handler = ComputeShaderHandler()
    shader = shader_handler.create(shader_settings[0])

    shader.use()
    shader.max_workgroup_size = 2
    shader.compute(3)

    assert shader == shader_handler.get("add")
