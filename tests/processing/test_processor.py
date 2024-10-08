from typing import Callable, Generator, List

import glfw
import numpy as np
import pytest

from joulegl.opengl_helper.base.config import ShaderConfig
from joulegl.opengl_helper.base.data_set import BaseShaderSet
from joulegl.opengl_helper.buffer import BufferObject, BufferType
from joulegl.opengl_helper.compute.shader import ComputeShader, ComputeShaderSetting
from joulegl.opengl_helper.vertex_data_handler import VertexDataHandler
from joulegl.processing.processor import ComputeProcessor
from joulegl.utility.glcontext import GLContext
from joulegl.utility.window import BaseWindow
from joulegl.utility.window_config import WindowConfig


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


class SampleDataHandler:
    def __init__(self, data: np.ndarray) -> None:
        self.data: np.ndarray = data
        self.buffer: BufferObject = BufferObject(
            buffer_type=BufferType.SHADER_STORAGE_BUFFER
        )

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
        shader_settings.extend([ComputeShaderSetting("add", ["add.comp"], [])])
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

        self.execute_funcs["add"] = generate_compute_func(self.shaders["add"])
        self.element_count_funcs["add"] = generate_element_count_func(self.sdh)

        self.create_sets(self.data_handler, "add")

    def process(self, set_name: str, config: ShaderConfig | None = None) -> None:
        current_set: BaseShaderSet = self.sets[set_name]
        current_set.set_uniform_data([("value", self.value, "float")])
        current_set.set_uniform_labeled_data(config)
        current_set.use()

    def delete(self) -> None:
        self.data_handler.delete()


def test_compute_processor(gl_context: GLContext) -> None:
    data = np.zeros(12, dtype=np.float32)
    sdh = SampleDataHandler(data)
    sdh.parse_to_buffer()
    sp = SampleProcessor(sdh)

    same_data = sdh.buffer.read()
    assert np.array_equal(data, same_data)

    sp.process("add")

    changed_data = sdh.buffer.read()

    assert not np.array_equal(data, changed_data)
    assert np.all(changed_data == 0.25)

    sp.value = 0.5

    sp.process("add")

    changed_data = sdh.buffer.read()

    assert not np.array_equal(data, changed_data)
    assert np.all(changed_data == 0.5)

    sp.delete()
    sdh.buffer.delete()
