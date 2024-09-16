from typing import Generator, Type
import numpy as np
import pytest

from OpenGL.GL import *
from joulegl.opengl_helper.buffer import (
    BufferObject,
    BufferType,
    OverflowingBufferObject,
)
from joulegl.opengl_helper.vertex_data_handler import (
    BaseDataHandler,
    OverflowingVertexDataHandler,
    VertexDataHandler,
)
from joulegl.utility.glcontext import GLContext


@pytest.fixture(scope="module")
def gl_context() -> Generator[GLContext, None, None]:
    context = GLContext()
    with context:
        yield context


@pytest.mark.parametrize(
    "data_handler",
    [
        VertexDataHandler,
        OverflowingVertexDataHandler,
    ],
)
def test_vertex_data_handler_empty(
    gl_context: GLContext, data_handler: Type[VertexDataHandler]
) -> None:
    data_handler = data_handler([])
    data_handler.set()

    assert glGetIntegerv(GL_VERTEX_ARRAY_BINDING) == data_handler.handle

    data_handler.delete()


@pytest.mark.parametrize("targeted", [True, False])
@pytest.mark.parametrize("buffer_divisor", [None, 1])
def test_vertex_data_handler(
    gl_context: GLContext, buffer_divisor: int | None, targeted: bool
) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    buffer.load(data)
    targeted_buffer = [(buffer, 2)] if targeted else []
    untargeted_buffer = [] if targeted else [buffer]
    data_handler = VertexDataHandler(
        targeted_buffer,
        [] if buffer_divisor is None else [(1, buffer_divisor)],
        untargeted_buffer,
    )
    data_handler.set()

    assert glGetIntegerv(GL_VERTEX_ARRAY_BINDING) == data_handler.handle
    if targeted:
        assert glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 2) == buffer.handle

    data_handler.delete()


@pytest.mark.parametrize("targeted", [True, False])
def test_vertex_data_handler_buffer_not_loaded(
    gl_context: GLContext, targeted: bool
) -> None:
    buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    data_handler = (
        VertexDataHandler([(buffer, 2)], [])
        if targeted
        else VertexDataHandler([], [], [buffer])
    )
    with pytest.raises(AssertionError) as e:
        data_handler.set()
    assert e.value.args[0] == "Buffer was not initalized with data!"

    data_handler.delete()


@pytest.mark.parametrize("buffer_divisor", [None, 1])
def test_overflowing_vertex_data_handler(
    gl_context: GLContext, buffer_divisor: int | None
) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    buffer.load(data)

    def split_data(data: np.ndarray, index: int, max_size: int, object_size: int):
        start = int(index * max_size / (object_size * 4))
        end = int((index + 1) * max_size / (object_size * 4))
        return data[start:end]

    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    overflowing_buffer = OverflowingBufferObject(split_data, object_size=1)
    overflowing_buffer.max_ssbo_size = 250 * 4  # X floats = 4 * X bytes
    overflowing_buffer.load(data)

    targeted_buffer = [(buffer, 4)]
    data_handler = OverflowingVertexDataHandler(
        targeted_buffer,
        [(overflowing_buffer, 0)],
        [] if buffer_divisor is None else [(1, buffer_divisor)],
    )
    data_handler.set()

    assert glGetIntegerv(GL_VERTEX_ARRAY_BINDING) == data_handler.handle
    assert (
        glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 0)
        == overflowing_buffer.handle
    )
    assert glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 4) == buffer.handle

    data_handler.set_range(2)
    assert (
        glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 0)
        == overflowing_buffer.overflowing_handles[0]
    )
    assert (
        glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 1)
        == overflowing_buffer.overflowing_handles[1]
    )
    assert glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 4) == buffer.handle

    data_handler.set_buffer(1)
    data_handler.set_range(2)
    assert (
        glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 0)
        == overflowing_buffer.overflowing_handles[1]
    )
    assert (
        glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 1)
        == overflowing_buffer.overflowing_handles[2]
    )
    assert glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 4) == buffer.handle

    data_handler.set_buffer(0)
    data_handler.set_consecutive()
    for i in range(4):
        handle = glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, i)
        assert handle == overflowing_buffer.overflowing_handles[i]
    assert glGetIntegeri_v(GL_SHADER_STORAGE_BUFFER_BINDING, 4) == buffer.handle

    data_handler.delete()


@pytest.mark.parametrize("targeted", [True, False])
def test_overflowing_vertex_data_handler_not_loaded(
    gl_context: GLContext, targeted: bool
) -> None:
    data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    buffer = BufferObject(buffer_type=BufferType.SHADER_STORAGE_BUFFER)
    # buffer.load(data)

    def split_data(data: np.ndarray, index: int, max_size: int, object_size: int):
        start = int(index * max_size / (object_size * 4))
        end = int((index + 1) * max_size / (object_size * 4))
        return data[start:end]

    data_size = 1000
    data = np.arange(data_size, dtype=np.float32)
    overflowing_buffer = OverflowingBufferObject(split_data, object_size=1)
    overflowing_buffer.max_ssbo_size = 250 * 4  # X floats = 4 * X bytes
    # overflowing_buffer.load(data)

    targeted_buffer = [(buffer, 4)]
    data_handler = OverflowingVertexDataHandler(
        targeted_buffer if targeted else [],
        [(overflowing_buffer, 0)],
        [],
    )

    with pytest.raises(AssertionError) as e:
        data_handler.set_range(2)
    assert e.value.args[0] == "Buffer was not initalized with data!"

    data_handler.delete()
