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
from joulegl.utility.glcontext import GLContext
from tests.rendering.test_renderer import SampleRenderer, ScreenQuadDataHandler


@pytest.fixture(scope="module")
def gl_context():
    context = GLContext()
    with context:
        yield context


@pytest.mark.parametrize(
    "buffer_type", [BufferType.SSBO, BufferType.ARRAY_BUFFER, BufferType.INDEX_BUFFER]
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
    original_buffer = BufferObject(buffer_type=BufferType.SSBO)
    assert not original_buffer.loaded
    original_buffer.load(data)

    buffer_copy = BufferCopy(original_buffer, buffer_type=BufferType.SSBO)
    assert buffer_copy.handle == original_buffer.handle
    assert buffer_copy.loaded
    assert np.array_equal(buffer_copy.read(), original_buffer.read())

    buffer_copy.delete()

    # test if deleting the copy does not affect the original buffer
    assert np.array_equal(data, original_buffer.read())
    original_buffer.delete()


def test_swapping_buffer_object(gl_context: GLContext) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = SwappingBufferObject(buffer_type=BufferType.SSBO)
    assert not buffer.loaded
    buffer.load(data)

    read_data = buffer.read()
    buffer.swap()
    swapped_data = buffer.read()

    assert np.array_equal(data, swapped_data)
    assert np.array_equal(read_data, swapped_data)

    buffer.clear()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)
    buffer.swap()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)

    buffer.delete()


@pytest.mark.parametrize("max_size", [250, 2000])
def test_overflowing_buffer_object(gl_context, max_size: int) -> None:
    def split_data(data: np.ndarray, index: int, max_size: int, object_size: int):
        start = int(index * max_size / (object_size * 4))
        end = int((index + 1) * max_size / (object_size * 4))
        return data[start:end]

    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    buffer = OverflowingBufferObject(split_data, object_size=1)
    buffer.max_ssbo_size = max_size * 4  # X floats = 4 * X bytes
    buffer.load(data)
    assert len(buffer.handle) == int(math.ceil(data_size / max_size))

    read_data = buffer.read()
    assert np.array_equal(data, read_data)

    buffer.clear()
    cleared_data = buffer.read()
    assert np.all(cleared_data == 0.0)
    assert len(cleared_data) == len(data)

    buffer.delete()


def test_buffer_data_too_big(gl_context: GLContext) -> None:
    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    buffer = BufferObject(buffer_type=BufferType.SSBO)
    buffer.max_ssbo_size = 1000
    with pytest.raises(Exception) as e:
        buffer.load(data)
    assert "Data to big for SSBO" in str(e.value)
    buffer.delete()


@pytest.mark.parametrize(
    "buffer_type", [BufferType.SSBO, BufferType.ARRAY_BUFFER, BufferType.INDEX_BUFFER]
)
def test_buffer_type_rendering(gl_context: GLContext, buffer_type: BufferType) -> None:
    data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler(buffer_type)
    renderer: SampleRenderer = SampleRenderer(data_handler, False)
    renderer.render(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    gl_context.window.swap()

    pixel_data = None
    glReadBuffer(GL_FRONT)
    try:
        pixel_data = np.frombuffer(
            glReadPixels(
                0,
                0,
                gl_context.window.config["width"],
                gl_context.window.config["height"],
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
            * gl_context.window.config["width"]
            * gl_context.window.config["height"],
            dtype=np.uint8,
        ),
    )

    renderer.delete()
    data_handler.buffer.delete()


def test_renderer_divisor(gl_context: GLContext) -> None:
    data_handler: ScreenQuadDataHandler = ScreenQuadDataHandler()
    renderer: SampleRenderer = SampleRenderer(data_handler, False, True)
    renderer.render(np.array([1.0, 0.0, 0.0], dtype=np.float32))
    gl_context.window.swap()

    pixel_data = None
    glReadBuffer(GL_FRONT)
    try:
        pixel_data = np.frombuffer(
            glReadPixels(
                0,
                0,
                gl_context.window.config["width"],
                gl_context.window.config["height"],
                GL_RGBA,
                GL_UNSIGNED_BYTE,
            ),
            dtype=np.uint8,
        )
    except Exception as e:
        pass

    width = gl_context.window.config["width"]
    height = gl_context.window.config["height"]
    pixel_data = pixel_data.reshape((height, width, 4))
    assert np.all(pixel_data[:, : width // 2, :3] == [255, 0, 0])
    assert np.all(pixel_data[:, width // 2 :, :3] == [0, 255, 0])

    renderer.delete()
    data_handler.buffer.delete()
