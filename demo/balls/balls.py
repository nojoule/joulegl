import os
import sys
from typing import Callable, List, Tuple

import glfw
import numpy as np

sys.path.append(os.getcwd())


from joulegl.opengl_helper.base.config import ShaderConfig
from joulegl.opengl_helper.base.data_set import BaseShaderSet
from joulegl.opengl_helper.base.shader_parser import ShaderParser
from joulegl.opengl_helper.buffer import BufferType, SwappingBufferObject
from joulegl.opengl_helper.compute.shader import ComputeShader, ComputeShaderSetting
from joulegl.opengl_helper.render.shader import RenderShaderSetting
from joulegl.opengl_helper.render.utility import (
    OglBlendingEquations,
    OglBlendingFactors,
    OglPrimitives,
    OGLRenderFunction,
    generate_render_function,
)
from joulegl.opengl_helper.vertex_data_handler import VertexDataHandler
from joulegl.processing.processor import ComputeProcessor
from joulegl.rendering.renderer import Renderer
from joulegl.utility.app import App
from joulegl.utility.camera import Camera, CameraPose
from joulegl.utility.performance import track_time


class BallData:
    def __init__(self, pos: np.ndarray, size: float) -> None:
        self.pos: np.ndarray = pos
        self.size = size
        self.data = [self.pos[0], self.pos[1], self.pos[2], self.size]


class BallDataHandler:
    def __init__(self) -> None:
        self.ball_data: List[BallData] = []
        self.balls_changed: bool = False
        self.data: List[float] = []
        self.buffer: SwappingBufferObject = SwappingBufferObject(
            buffer_type=BufferType.SHADER_STORAGE_BUFFER
        )

    def get_buffer_points(self) -> int:
        return len(self.ball_data)

    def parse_to_buffer(self) -> None:
        self.data = [float(value) for ball in self.ball_data for value in ball.data]
        self.buffer.load(np.array(self.data, dtype=np.float32))

    def apply(self, balls: List[BallData]) -> None:
        self.balls_changed = True
        self.ball_data = balls
        self.parse_to_buffer()

    def swap(self) -> None:
        self.buffer.swap()


class BallRenderer(Renderer):
    def __init__(self, bdh: BallDataHandler) -> None:
        shader_parser: ShaderParser = ShaderParser()
        super().__init__(shader_parser=shader_parser)

        self.bdh = bdh

        shader_settings: List[RenderShaderSetting] = []
        shader_settings.extend(
            [
                RenderShaderSetting(
                    "sphere",
                    [
                        "ball_impostor.vert",
                        "sphere.frag",
                        "point_to_ball_impostor.geom",
                    ],
                    ["screen_width", "screen_height"],
                ),
                RenderShaderSetting(
                    "triangle",
                    [
                        "basic.vert",
                        "basic.frag",
                    ],
                    ["screen_width", "screen_height"],
                ),
            ]
        )
        self.set_shader(shader_settings)

        self.data_handler: VertexDataHandler = VertexDataHandler([(self.bdh.buffer, 0)])

        def generate_element_count_func(bdh: BallDataHandler) -> Callable:
            def element_count_func() -> int:
                return bdh.get_buffer_points()

            return element_count_func

        self.execute_funcs["sphere"] = generate_render_function(
            OGLRenderFunction.ARRAYS, OglPrimitives.POINTS, depth_test=True
        )
        self.execute_funcs["triangle"] = generate_render_function(
            OGLRenderFunction.ARRAYS,
            OglPrimitives.TRIANGLES,
            depth_test=False,
            add_blending=[
                OglBlendingFactors.SRC_ALPHA,
                OglBlendingFactors.ONE_MINUS_SRC_ALPHA,
                OglBlendingEquations.FUNC_ADD,
                OglBlendingEquations.FUNC_ADD,
            ],
        )
        self.element_count_funcs["sphere"] = generate_element_count_func(self.bdh)
        self.element_count_funcs["triangle"] = generate_element_count_func(self.bdh)

        self.create_sets(self.data_handler, "sphere")
        self.create_sets(self.data_handler, "triangle")

    def render(
        self, set_name: str, cam: Camera, config: ShaderConfig | None = None
    ) -> None:
        current_set: BaseShaderSet = self.sets[set_name]
        current_set.set_uniform_data(
            [("projection", cam.projection, "mat4"), ("view", cam.view, "mat4")]
        )
        current_set.set_uniform_labeled_data(config)
        current_set.use(True)

    def delete(self) -> None:
        self.data_handler.delete()


class BallProcessor(ComputeProcessor):
    def __init__(self, bdh: BallDataHandler) -> None:
        shader_parser: ShaderParser = ShaderParser()
        super().__init__(shader_parser=shader_parser)

        self.bdh = bdh

        shader_settings: List[ComputeShaderSetting] = []
        shader_settings.extend([ComputeShaderSetting("noise", ["ball_noise.comp"], [])])
        self.set_shader(shader_settings)

        self.data_handler: VertexDataHandler = VertexDataHandler([(self.bdh.buffer, 0)])

        def generate_element_count_func(bdh: BallDataHandler) -> Callable:
            def element_count_func() -> int:
                return bdh.get_buffer_points()

            return element_count_func

        def generate_compute_func(compute_shader: ComputeShader) -> Callable:
            def compute_func(element_count: int, _=None) -> None:
                compute_shader.compute(element_count, barrier=True)

            return compute_func

        self.execute_funcs["noise"] = generate_compute_func(self.shaders["noise"])
        self.element_count_funcs["noise"] = generate_element_count_func(self.bdh)

        self.create_sets(self.data_handler, "noise")

    def process(self, set_name: str, config: ShaderConfig | None = None) -> None:
        current_set: BaseShaderSet = self.sets[set_name]
        """current_set.set_uniform_data([("projection", cam.projection, "mat4"),
                                      ("view", cam.view, "mat4")])"""
        current_set.set_uniform_labeled_data(config)
        current_set.use()

        self.bdh.swap()

    def delete(self) -> None:
        self.data_handler.delete()


def generate_random_balls_in_a_sphere(
    area: Tuple[int, int, int], ball_size: float
) -> List[BallData]:
    balls: List[BallData] = []
    for x in range(area[0] * 10):
        x = x / 10.0
        sqr_off_x = abs(x - area[0] * 0.5) * abs(x - area[0] * 0.5)
        for y in range(area[1] * 10):
            y = y / 10.0
            sqr_off_y = abs(y - area[1] * 0.5) * abs(y - area[1] * 0.5)
            for z in range(area[2] * 10):
                z = z / 10.0
                if (
                    sqr_off_x
                    + sqr_off_y
                    + abs(z - area[2] * 0.5) * abs(z - area[2] * 0.5)
                    <= area[0] * area[0] * 0.25
                ):
                    balls.append(
                        BallData(
                            np.array([x, y, z], dtype=np.float32),
                            ball_size,
                        )
                    )
    return balls


class BallApp(App):
    def __init__(self) -> None:
        super().__init__("Ball Demo")

        self.bdh: BallDataHandler = BallDataHandler()
        self.bdh.apply(generate_random_balls_in_a_sphere((10, 10, 10), 0.1))
        self.br: BallRenderer = BallRenderer(self.bdh)
        self.bp: BallProcessor = BallProcessor(self.bdh)
        self.br_config: ShaderConfig = ShaderConfig()
        self.set_cam(np.array([5.0, 5.0, 5.0], dtype=np.float32), 60.0, CameraPose.LEFT)
        self.active_renderer = "triangle"

    @track_time(app_name="ball_demo")
    def render(self) -> None:
        self.bp.process("noise")
        self.br.render(self.active_renderer, self.window.cam, self.br_config)
        if self.frame_count % (self.fps * 60) == 0:
            self.bdh.parse_to_buffer()

    def key_input(self, key, scancode, action, mods) -> bool | None:
        if key == glfw.KEY_SPACE and action == glfw.RELEASE:
            if self.active_renderer == "sphere":
                self.active_renderer = "triangle"
            else:
                self.active_renderer = "sphere"
        if key == glfw.KEY_C and action == glfw.RELEASE:
            self.bdh.parse_to_buffer()
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(self.window.window_handle, True)
        return False


if __name__ == "__main__":
    app = BallApp()
    app.run()
