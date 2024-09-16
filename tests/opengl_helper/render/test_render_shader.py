from typing import Generator

import numpy as np
import pytest
from OpenGL.GL import *

from joulegl.opengl_helper.frame_buffer import FrameBufferObject
from joulegl.opengl_helper.render.shader import RenderShaderSetting
from joulegl.opengl_helper.render.shader_handler import RenderShaderHandler
from joulegl.opengl_helper.texture import Texture
from joulegl.utility.glcontext import GLContext
from tests.rendering.test_renderer import SampleRenderer, ScreenQuadDataHandler


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


def test_wrong_shader_file_count() -> None:
    with pytest.raises(Exception) as e:
        RenderShaderSetting("id", ["vertex", "fragment", "geometry", "extra"])
    assert (
        e.value.args[0]
        == "Can't handle number of shaders for a program (either 2 or 3 with geometry shader)."
    )


def test_renderer_geometry(gl_context: GLContext) -> None:
    data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler()
    renderer: SampleRenderer = SampleRenderer(data_handler, False, None, True)
    frame_buffer = FrameBufferObject(
        gl_context.window.config["width"], gl_context.window.config["height"]
    )
    frame_buffer.bind()
    renderer.render(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    gl_context.window.swap()

    pixel_data = frame_buffer.read()

    expected_array = np.array(
        [255, 0, 0, 255]
        * gl_context.window.config["width"]
        * gl_context.window.config["height"],
        dtype=np.uint8,
    )
    assert np.array_equal(
        pixel_data,
        expected_array,
    )

    renderer.delete()
    data_handler.buffer.delete()
    frame_buffer.delete()


def test_set_textures(gl_context: GLContext) -> None:

    texture = Texture(100, 100)
    texture.setup(np.array([255] * 100 * 100 * 4, dtype=np.uint8), 0)

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
    render_shader.set_textures([(texture, "read_only", 0)])

    texture, flag, position = render_shader.textures[0]
    assert flag == "read_only"
    assert position == 0
    assert texture.width == 100
    assert texture.height == 100

    render_shader.use()
    assert glGetIntegerv(GL_TEXTURE_BINDING_2D) == texture.ogl_handle
