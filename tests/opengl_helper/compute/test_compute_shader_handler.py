from typing import Generator

import pytest

from joulegl.opengl_helper.base.shader import ShaderSetting
from joulegl.opengl_helper.compute.shader import ComputeShader, ComputeShaderSetting
from joulegl.opengl_helper.compute.shader_handler import ComputeShaderHandler
from joulegl.utility.glcontext import GLContext


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


def test_compute_shader_handler(gl_context: GLContext) -> None:
    shader_setting = ComputeShaderSetting("add_comp", ["add.comp"])

    shader_handler = ComputeShaderHandler()
    shader = shader_handler.create(shader_setting, None)
    assert isinstance(shader, ComputeShader)
    assert shader.name == "add_comp"


def test_compute_shader_handler_wrong_type(gl_context: GLContext) -> None:
    shader_setting = ShaderSetting("test")
    shader_handler = ComputeShaderHandler()
    with pytest.raises(ValueError) as e:
        shader_handler.create(shader_setting, None)
    assert e.value.args[0] == "ComputeShaderSetting required for ComputeShaderHandler"


def test_compute_shader_handler_twice(gl_context: GLContext) -> None:
    shader_setting = ComputeShaderSetting("add_comp", ["add.comp"])

    shader_handler = ComputeShaderHandler()
    assert "add_comp" not in shader_handler.shader_list

    shader = shader_handler.create(shader_setting, None)
    assert isinstance(shader, ComputeShader)
    assert shader.name == "add_comp"
    assert shader_handler.shader_list["add_comp"] == shader

    new_shader = shader_handler.create(shader_setting, None)
    assert new_shader == shader
    assert shader_handler.shader_list["add_comp"] == shader
