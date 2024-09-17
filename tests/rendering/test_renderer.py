from typing import Callable, Generator, List

import numpy as np
import pytest

from joulegl.opengl_helper.base.data_set import BaseShaderSet
from joulegl.opengl_helper.buffer import BufferObject, BufferType
from joulegl.opengl_helper.frame_buffer import FrameBufferObject
from joulegl.opengl_helper.render.shader import RenderShaderSetting
from joulegl.opengl_helper.render.utility import (
    OglPrimitives,
    OGLRenderFunction,
    generate_render_function,
)
from joulegl.opengl_helper.vertex_data_handler import VertexDataHandler
from joulegl.rendering.renderer import Renderer
from joulegl.utility.glcontext import GLContext


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


class ScreenQuadDataHandler:
    def __init__(
        self,
        buffer_type: BufferType = BufferType.ARRAY_BUFFER,
        use_geometry: bool = False,
    ) -> None:
        self.use_geometry = use_geometry
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
        if use_geometry:
            self.data = np.array(
            [
                0.0, 0.0, 0.0, 1.0
            ],
            dtype=np.float32,
        )

        # fmt: on
        self.buffer: BufferObject = BufferObject(buffer_type=buffer_type)
        self.parse_to_buffer()

    def get_buffer_points(self) -> int:
        return 2 if not self.use_geometry else 1

    def parse_to_buffer(self) -> None:
        self.buffer.load(self.data)


class ScreenQuadColorDataHandler:
    def __init__(self, buffer_type: BufferType = BufferType.ARRAY_BUFFER) -> None:
        # fmt: off
        self.data: np.ndarray = np.array(
            [
                1.0, 0.0, 0.0, 1.0,
                0.0, 1.0, 0.0, 1.0,
            ],
            dtype=np.float32,
        )
        # fmt: on
        self.buffer: BufferObject = BufferObject(buffer_type=buffer_type, object_size=0)
        self.parse_to_buffer()

    def get_buffer_points(self) -> int:
        return 2

    def parse_to_buffer(self) -> None:
        self.buffer.load(self.data)


class SampleRenderer(Renderer):
    def __init__(
        self,
        data: ScreenQuadDataHandler,
        use_implicit_set_name: bool = True,
        color_buffer: ScreenQuadColorDataHandler | None = None,
        use_geometry: bool = False,
    ) -> None:
        super().__init__()

        self.data: ScreenQuadDataHandler = data
        if color_buffer:
            self.color_data: ScreenQuadColorDataHandler = color_buffer

        shader_settings: List[RenderShaderSetting] = []
        if color_buffer:
            shader_settings.extend(
                [
                    RenderShaderSetting(
                        "screen_quad",
                        [
                            "screen_quad_color.vert",
                            "screen_quad_color.frag",
                        ],
                    ),
                ]
            )
        else:
            shader_src_list = ["screen_quad.vert", "screen_quad.frag"]
            if use_geometry:
                shader_src_list = [
                    "screen_quad_geom.vert",
                    "screen_quad.frag",
                    "screen_quad_geom.geom",
                ]
            shader_settings.extend(
                [
                    RenderShaderSetting("screen_quad", shader_src_list),
                ]
            )
        self.set_shader(shader_settings)

        if color_buffer:
            self.data_handler: VertexDataHandler = VertexDataHandler(
                [(self.data.buffer, 0), (self.color_data.buffer, 1)], [(0, 0), (1, 1)]
            )
        else:
            self.data_handler: VertexDataHandler = VertexDataHandler(
                [(self.data.buffer, 0)]
            )

        def generate_element_count_func(dh: ScreenQuadDataHandler) -> Callable:
            count = 2 if color_buffer else 1 if use_geometry else 6

            def element_count_func() -> int:
                return count  # dh.get_buffer_points()

            return element_count_func

        if color_buffer:
            self.execute_funcs["screen_quad"] = generate_render_function(
                OGLRenderFunction.ARRAYS_INSTANCED,
                OglPrimitives.TRIANGLES,
                instance_vertices=6,
            )
        else:
            if use_geometry:
                self.execute_funcs["screen_quad"] = generate_render_function(
                    OGLRenderFunction.ARRAYS, OglPrimitives.POINTS
                )
            else:
                self.execute_funcs["screen_quad"] = generate_render_function(
                    OGLRenderFunction.ARRAYS, OglPrimitives.TRIANGLES
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
def test_renderer(gl_context: GLContext, use_implicit_set_name: bool) -> None:
    data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler()
    renderer: SampleRenderer = SampleRenderer(data_handler, use_implicit_set_name, None)
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
