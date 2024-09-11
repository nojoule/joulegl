from typing import Callable, List

import numpy as np
import pytest
from OpenGL.GL import *

from joulegl.opengl_helper.base.data_set import BaseShaderSet
from joulegl.opengl_helper.buffer import BufferObject, BufferType
from joulegl.opengl_helper.render.shader import RenderShaderSetting
from joulegl.opengl_helper.render.utility import (
    OGLRenderFunction,
    generate_render_function,
)
from joulegl.opengl_helper.vertex_data_handler import VertexDataHandler
from joulegl.rendering.renderer import Renderer
from joulegl.utility.glcontext import GLContext


class ScreenQuadDataHandler:
    def __init__(self) -> None:
        # fmt: off
        self.data: np.ndarray = np.array(
            [
                -1.0, -1.0, 0.0, 1.0,
                1.0, -1.0, 0.0, 1.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, -1.0, 0.0, 1.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, 1.0, 0.0, 1.0,
            ],
            dtype=np.float32,
        )
        # fmt: on
        self.buffer: BufferObject = BufferObject(buffer_type=BufferType.ARRAY_BUFFER)
        self.parse_to_buffer()

    def get_buffer_points(self) -> int:
        return 2

    def parse_to_buffer(self) -> None:
        self.buffer.load(self.data)


class SampleRenderer(Renderer):
    def __init__(
        self, data: ScreenQuadDataHandler, use_implicit_set_name: bool = True
    ) -> None:
        super().__init__()

        self.data: ScreenQuadDataHandler = data

        shader_settings: List[RenderShaderSetting] = []
        shader_settings.extend(
            [
                RenderShaderSetting(
                    "screen_quad",
                    [
                        "screen_quad.vert",
                        "screen_quad.frag",
                    ],
                ),
            ]
        )
        self.set_shader(shader_settings)

        self.data_handler: VertexDataHandler = VertexDataHandler(
            [(self.data.buffer, 0)]
        )

        def generate_element_count_func(dh: ScreenQuadDataHandler) -> Callable:
            def element_count_func() -> int:
                return 6  # dh.get_buffer_points()

            return element_count_func

        self.execute_funcs["screen_quad"] = generate_render_function(
            OGLRenderFunction.ARRAYS, GL_TRIANGLES
        )
        self.element_count_funcs["screen_quad"] = generate_element_count_func(self.data)

        if use_implicit_set_name:
            self.create_sets(self.data_handler, "screen_quad")
        else:
            self.create_sets(
                self.data_handler,
                {"screen_quad": ("screen_quad", "screen_quad", "screen_quad")},
            )

    def render(self, color: np.ndarray) -> None:
        current_set: BaseShaderSet = self.sets["screen_quad"]
        current_set.set_uniform_labeled_data(None)
        current_set.set_uniform_data([("color", color, "vec3")])
        current_set.use(True)

    def delete(self) -> None:
        self.data_handler.delete()


@pytest.mark.parametrize("use_implicit_set_name", [True, False])
def test_renderer(use_implicit_set_name: bool) -> None:
    context = GLContext()
    with context:
        data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler()
        renderer: SampleRenderer = SampleRenderer(data_handler, use_implicit_set_name)
        renderer.render(np.array([1.0, 0.0, 0.0], dtype=np.float32))
        context.window.swap()

        pixel_data = None
        glReadBuffer(GL_FRONT)
        try:
            pixel_data = np.frombuffer(
                glReadPixels(
                    0,
                    0,
                    context.window.config["width"],
                    context.window.config["height"],
                    GL_RGBA,
                    GL_UNSIGNED_BYTE,
                ),
                dtype=np.uint8,
            )
        except Exception as e:
            pass

        assert np.array_equal(
            pixel_data,
            np.array(
                [255, 0, 0, 255]
                * context.window.config["width"]
                * context.window.config["height"],
                dtype=np.uint8,
            ),
        )

        renderer.delete()
        data_handler.buffer.delete()
