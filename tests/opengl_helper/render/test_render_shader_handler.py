from typing import Generator

import pytest

from joulegl.opengl_helper.base.shader import ShaderSetting
from joulegl.opengl_helper.render.shader import RenderShader, RenderShaderSetting
from joulegl.opengl_helper.render.shader_handler import RenderShaderHandler
from joulegl.utility.glcontext import GLContext


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


def test_render_shader_handler(gl_context: GLContext) -> None:
    shader_setting = RenderShaderSetting(
        "screen_quad", ["screen_quad.vert", "screen_quad.frag"]
    )

    shader_handler = RenderShaderHandler()
    shader = shader_handler.create(shader_setting, None)
    assert isinstance(shader, RenderShader)
    assert shader.name == "screen_quad"


def test_render_shader_handler_wrong_type(gl_context: GLContext) -> None:
    shader_setting = ShaderSetting("test")
    shader_handler = RenderShaderHandler()
    with pytest.raises(ValueError) as e:
        shader_handler.create(shader_setting, None)
    assert e.value.args[0] == "RenderShaderSetting required for RenderShaderHandler"


def test_render_shader_handler_twice(gl_context: GLContext) -> None:
    shader_setting = RenderShaderSetting(
        "screen_quad", ["screen_quad.vert", "screen_quad.frag"]
    )

    shader_handler = RenderShaderHandler()
    assert "screen_quad" not in shader_handler.shader_list

    shader = shader_handler.create(shader_setting, None)
    assert isinstance(shader, RenderShader)
    assert shader.name == "screen_quad"
    assert shader_handler.shader_list["screen_quad"] == shader

    new_shader = shader_handler.create(shader_setting, None)
    assert new_shader == shader
    assert shader_handler.shader_list["screen_quad"] == shader
