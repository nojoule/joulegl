from typing import Any, Callable, Generator, List, Tuple

import pytest
from OpenGL.GL import *

from joulegl.opengl_helper.base.config import ShaderConfig
from joulegl.opengl_helper.base.shader import ShaderSetting, uniform_setter_function
from joulegl.opengl_helper.render.shader import RenderShader, RenderShaderSetting
from joulegl.opengl_helper.render.shader_handler import RenderShaderHandler
from joulegl.opengl_helper.texture import Texture
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


@pytest.mark.parametrize("patching", [True, False])
@pytest.mark.parametrize("not_listed", [True, False])
def test_set_uniform_labeled_data(
    gl_context: GLContext,
    monkeypatch: pytest.MonkeyPatch,
    not_listed: bool,
    patching: bool,
) -> None:
    settings = [
        ("test_float", 1.0, "float"),
        ("test_vec3", [1.0, 0.0, 0.0], "vec3"),
        ("test_mat4", [1.0, 0.0, 0.0, 0.0], "mat4"),
        ("test_int", 1, "int"),
        ("test_ivec3", [1, 0, 0], "ivec3"),
        ("test_not_in_shader", 1, "int"),
    ]

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

    if patching:

        def dummy_set_uniform_data(data: List[Tuple[str, Any, Any]]) -> None:
            if not_listed:
                assert data == []
            else:
                assert data == settings

        monkeypatch.setattr(render_shader, "set_uniform_data", dummy_set_uniform_data)

    render_shader.set_uniform_label(
        [
            "test_float",
            "test_vec3",
            "test_mat4",
            "test_int",
            "test_ivec3",
            "test_not_in_shader",
        ]
    )
    shader_config = ShaderConfig()

    shader_list = ["no_screen_quad"] if not_listed else ["screen_quad"]
    shader_config.set_items(
        [
            ("test_float", shader_list, "float", 1.0),
            ("test_vec3", shader_list, "vec3", [1.0, 0.0, 0.0]),
            ("test_mat4", shader_list, "mat4", [1.0, 0.0, 0.0, 0.0]),
            ("test_int", shader_list, "int", 1),
            ("test_ivec3", shader_list, "ivec3", [1, 0, 0]),
            ("test_not_in_shader", shader_list, "int", 1),
            ("test_ignore", shader_list, "int", 1),
        ]
    )
    render_shader.set_uniform_labeled_data(shader_config)

    if not patching:
        if not_listed:
            for setting in settings:
                assert setting[0] not in render_shader.uniform_cache
                assert "test_not_in_shader" not in render_shader.uniform_ignore_labels
        else:
            for setting in settings:
                if setting[0] == "test_not_in_shader":
                    assert setting[0] not in render_shader.uniform_cache
            assert "test_not_in_shader" in render_shader.uniform_ignore_labels

    render_shader.set_uniform_labeled_data(shader_config)

    if not patching:
        if not_listed:
            for setting in settings:
                assert setting[0] not in render_shader.uniform_cache
                assert "test_not_in_shader" not in render_shader.uniform_ignore_labels
        else:
            for setting in settings:
                if setting[0] == "test_not_in_shader":
                    assert setting[0] not in render_shader.uniform_cache
            assert "test_not_in_shader" in render_shader.uniform_ignore_labels


def test_set_textures(gl_context: GLContext) -> None:
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
    render_shader.set_textures([(Texture(100, 100), "read_only", 0)])

    texture, flag, position = render_shader.textures[0]
    assert flag == "read_only"
    assert position == 0
    assert texture.width == 100
    assert texture.height == 100
