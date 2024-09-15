import math

import numpy as np
import pytest
from OpenGL.GL import *

from joulegl.opengl_helper.buffer import (
    BufferCopy,
    BufferObject,
    BufferType,
    OverflowingBufferObject,
    SwappingBufferObject,
)
from joulegl.opengl_helper.frame_buffer import FrameBufferObject
from joulegl.utility.glcontext import GLContext
from tests.rendering.test_renderer import (
    SampleRenderer,
    ScreenQuadColorDataHandler,
    ScreenQuadDataHandler,
)


@pytest.fixture(scope="module")
def gl_context():
    context = GLContext()
    with context:
        yield context


@pytest.mark.parametrize(
    "buffer_type",
    [
        BufferType.SHADER_STORAGE_BUFFER,
        BufferType.ARRAY_BUFFER,
        BufferType.INDEX_BUFFER,
    ],
)
def test_buffer_object(gl_context: GLContext, buffer_type: BufferType) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = BufferObject(buffer_type=buffer_type)
    buffer.load(data)

    read_data = buffer.read()
    assert np.array_equal(data, read_data)

    buffer.clear()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)

    buffer.delete()


def test_buffer_copy(gl_context: GLContext) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    original_buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    assert not original_buffer.loaded
    original_buffer.load(data)

    buffer_copy = BufferCopy(
        original_buffer, buffer_type=BufferType.SHADER_STORAGE_BUFFER
    )
    assert buffer_copy.handle == original_buffer.handle
    assert buffer_copy.loaded
    assert np.array_equal(buffer_copy.read(), original_buffer.read())

    buffer_copy.delete()

    # test if deleting the copy does not affect the original buffer
    assert np.array_equal(data, original_buffer.read())
    original_buffer.delete()


def test_swapping_buffer_object(gl_context: GLContext) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = SwappingBufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    assert not buffer.loaded
    buffer.load(data)

    read_data = buffer.read()
    buffer.swap()
    swapped_data = buffer.read()

    assert np.array_equal(data, swapped_data)
    assert np.array_equal(read_data, swapped_data)

    buffer.swap()
    buffer.bind(0, False)
    handle = glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 0)
    assert handle == buffer.handle
    handle = glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 1)
    assert handle == buffer.swap_handle
    read_data = np.frombuffer(
        glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, buffer.size),
        dtype=buffer.data.dtype,
    )
    assert np.array_equal(read_data, data)

    buffer.bind(0, True)
    handle = glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 0)
    assert handle == buffer.handle

    buffer.clear()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)
    buffer.swap()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)

    buffer.delete()


@pytest.mark.parametrize("max_size", [250, 2000])
def test_overflowing_buffer_object(gl_context: GLContext, max_size: int) -> None:
    def split_data(data: np.ndarray, index: int, max_size: int, object_size: int):
        start = int(index * max_size / (object_size * 4))
        end = int((index + 1) * max_size / (object_size * 4))
        return data[start:end]

    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    buffer = OverflowingBufferObject(split_data, object_size=1)
    buffer.max_ssbo_size = max_size * 4  # X floats = 4 * X bytes
    buffer.load(data)
    assert len(buffer.overflowing_handles) == int(math.ceil(data_size / max_size))

    for i in range(len(buffer.overflowing_handles)):
        assert buffer.get_objects(i) == min(max_size, data_size)

    read_data = buffer.read()
    assert np.array_equal(data, read_data)

    buffer.clear()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)
    assert len(cleared_data) == len(data)

    buffer.delete()


def test_overflowing_buffer_object_binding(gl_context: GLContext) -> None:
    max_size = 250

    def split_data(data: np.ndarray, index: int, max_size: int, object_size: int):
        start = int(index * max_size / (object_size * 4))
        end = int((index + 1) * max_size / (object_size * 4))
        return data[start:end]

    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    buffer = OverflowingBufferObject(split_data, object_size=1)
    buffer.max_ssbo_size = max_size * 4  # X floats = 4 * X bytes
    buffer.load(data)
    assert len(buffer.overflowing_handles) == int(math.ceil(data_size / max_size))

    for i in range(len(buffer.overflowing_handles)):
        buffer.bind_single(i, 0)
        read_data = np.frombuffer(
            glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, buffer.size),
            dtype=buffer.data.dtype,
        )
        assert np.array_equal(split_data(data, i, max_size * 4, 1), read_data)

    buffer.bind_consecutive(0)
    for i in range(len(buffer.overflowing_handles)):
        handle = glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, i)
        assert handle == buffer.overflowing_handles[i]

    buffer.delete()


def test_overflowing_buffer_dynamically_generate_handles(gl_context: GLContext) -> None:
    def split_data(data: np.ndarray, index: int, max_size: int, object_size: int):
        start = int(index * max_size / (object_size * 4))
        end = int((index + 1) * max_size / (object_size * 4))
        return data[start:end]

    data_size = 1000
    buffer = OverflowingBufferObject(split_data, object_size=1)
    buffer.max_ssbo_size = 250 * 4  # 250 floats = 4 * 250 bytes
    buffer.load_empty(np.float32, data_size)
    assert len(buffer.overflowing_handles) == int(math.ceil(data_size / 250))

    read_data = buffer.read()
    assert np.array_equal(np.zeros([data_size], dtype=np.float32), read_data)

    buffer.delete()


def test_buffer_data_too_big(gl_context: GLContext) -> None:
    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    buffer.max_ssbo_size = 1000
    with pytest.raises(Exception) as e:
        buffer.load(data)
    assert "Data to big for SSBO" in str(e.value)
    buffer.delete()


@pytest.mark.parametrize(
    "buffer_type",
    [
        BufferType.SHADER_STORAGE_BUFFER,
        BufferType.ARRAY_BUFFER,
    ],
)
def test_buffer_type_rendering(gl_context: GLContext, buffer_type: BufferType) -> None:
    data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler(buffer_type)
    renderer: SampleRenderer = SampleRenderer(data_handler, False)

    frame_buffer = FrameBufferObject(
        gl_context.window.config["width"], gl_context.window.config["height"]
    )
    frame_buffer.bind()

    renderer.render(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    gl_context.window.swap()

    pixel_data = frame_buffer.read()

    assert np.array_equal(
        pixel_data,
        np.array(
            [255, 0, 0, 255]
            * gl_context.window.config["width"]
            * gl_context.window.config["height"],
            dtype=np.uint8,
        ),
    )

    renderer.delete()
    data_handler.buffer.delete()
    frame_buffer.delete()


@pytest.mark.parametrize(
    "buffer_type",
    [
        BufferType.SHADER_STORAGE_BUFFER,
        BufferType.ARRAY_BUFFER,
    ],
)
def test_renderer_divisor(gl_context: GLContext, buffer_type: BufferType) -> None:
    data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler()
    renderer: SampleRenderer = SampleRenderer(
        data_handler, False, ScreenQuadColorDataHandler(buffer_type)
    )
    frame_buffer = FrameBufferObject(
        gl_context.window.config["width"], gl_context.window.config["height"]
    )
    frame_buffer.bind()

    renderer.render(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    gl_context.window.swap()

    pixel_data = frame_buffer.read()

    width = gl_context.window.config["width"]
    height = gl_context.window.config["height"]
    pixel_data = pixel_data.reshape((height, width, 4))
    assert np.all(pixel_data[:, : width // 2, :3] == [255, 0, 0])
    assert np.all(pixel_data[:, width // 2 :, :3] == [0, 255, 0])

    renderer.delete()
    data_handler.buffer.delete()
    frame_buffer.delete()


def test_ssbo_buffer_copy(gl_context: GLContext) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    buffer.load(data)

    buffer_copy = BufferCopy(buffer, buffer_type=BufferType.ARRAY_BUFFER)
    assert buffer_copy.handle == buffer.handle
    assert buffer_copy.loaded
    assert np.array_equal(buffer_copy.read(), buffer.read())

    buffer.delete()
