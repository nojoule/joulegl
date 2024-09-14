from typing import Any, Callable, Generator

import pytest
from OpenGL.GL import *

from joulegl.opengl_helper.base.shader import ShaderSetting, uniform_setter_function
from joulegl.opengl_helper.render.shader import RenderShaderSetting
from joulegl.opengl_helper.render.shader_handler import RenderShaderHandler
from joulegl.utility.glcontext import GLContext


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


def test_uniform_setter_function() -> None:
    assert uniform_setter_function("float")
    assert uniform_setter_function("vec3")
    assert uniform_setter_function("mat4")
    assert uniform_setter_function("int")
    assert uniform_setter_function("ivec3")

    with pytest.raises(Exception):
        uniform_setter_function("invalid")


def test_shader_setting() -> None:
    shader_setting = ShaderSetting("test", ["uniform1", "uniform2"])
    assert shader_setting.id_name == "test"
    assert shader_setting.uniform_labels == ["uniform1", "uniform2"]


def test_set_uniform(gl_context: GLContext) -> None:
    shader_settings = [
        RenderShaderSetting(
            "screen_quad",
            [
                "uniform_test.vert",
                "screen_quad.frag",
            ],
        ),
    ]
    shader_handler = RenderShaderHandler()
    render_shader = shader_handler.create(shader_settings[0])

    render_shader.set_uniform_data(
        [
            ("test_float", 1.0, "float"),
            ("test_vec3", [1.0, 0.0, 0.0], "vec3"),
            ("test_mat4", [1.0, 0.0, 0.0, 0.0], "mat4"),
            ("test_int", 1, "int"),
            ("test_ivec3", [1, 0, 0], "ivec3"),
        ]
    )
    render_shader.use()
