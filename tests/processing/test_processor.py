from typing import Callable, List

import glfw
import numpy as np

from joulegl.opengl_helper.base.config import ShaderConfig
from joulegl.opengl_helper.base.data_set import BaseShaderSet
from joulegl.opengl_helper.buffer import BufferObject, BufferType
from joulegl.opengl_helper.compute.shader import ComputeShader, ComputeShaderSetting
from joulegl.opengl_helper.vertex_data_handler import VertexDataHandler
from joulegl.processing.processor import ComputeProcessor
from joulegl.utility.window import BaseWindow
from joulegl.utility.window_config import WindowConfig


class SampleDataHandler:
    def __init__(self, data: np.ndarray) -> None:
        self.data: np.ndarray = data
        self.buffer: BufferObject = BufferObject(buffer_type=BufferType.SSBO)

    def get_buffer_points(self) -> int:
        return len(self.data)

    def parse_to_buffer(self) -> None:
        self.buffer.load(self.data)


class SampleProcessor(ComputeProcessor):
    def __init__(self, sdh: SampleDataHandler) -> None:
        super().__init__()

        self.sdh = sdh
        self.value = 0.25

        shader_settings: List[ComputeShaderSetting] = []
        shader_settings.extend([ComputeShaderSetting("noise", ["noise.comp"], [])])
        self.set_shader(shader_settings)

        self.data_handler: VertexDataHandler = VertexDataHandler([(self.sdh.buffer, 0)])

        def generate_element_count_func(sdh: SampleDataHandler) -> Callable:
            def element_count_func() -> int:
                return sdh.get_buffer_points()

            return element_count_func

        def generate_compute_func(compute_shader: ComputeShader) -> Callable:
            def compute_func(element_count: int, _=None) -> None:
                compute_shader.compute(element_count, barrier=True)

            return compute_func

        self.execute_funcs["noise"] = generate_compute_func(self.shaders["noise"])
        self.element_count_funcs["noise"] = generate_element_count_func(self.sdh)

        self.create_sets(self.data_handler)

    def process(self, set_name: str, config: ShaderConfig | None = None) -> None:
        current_set: BaseShaderSet = self.sets[set_name]
        current_set.set_uniform_data([("value", self.value, "float")])
        current_set.set_uniform_labeled_data(config)
        current_set.use()

    def delete(self) -> None:
        self.data_handler.delete()


def test_compute_processor() -> None:
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = BaseWindow(WindowConfig())
    window.activate()

    data = np.zeros(12, dtype=np.float32)
    sdh = SampleDataHandler(data)
    sdh.parse_to_buffer()
    sp = SampleProcessor(sdh)

    same_data = sdh.buffer.read()
    assert np.array_equal(data, same_data)

    sp.process("noise")

    changed_data = sdh.buffer.read()

    assert not np.array_equal(data, changed_data)
    assert np.all(changed_data == 0.25)

    sp.value = 0.5

    sp.process("noise")

    changed_data = sdh.buffer.read()

    assert not np.array_equal(data, changed_data)
    assert np.all(changed_data == 0.5)

    sp.delete()
    sdh.buffer.delete()
    window.destroy()
