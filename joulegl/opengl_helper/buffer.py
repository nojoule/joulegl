import logging
import math
from enum import Enum
from typing import Callable, List, Tuple

import numpy as np
from OpenGL.GL import *


class BufferType(Enum):
    ARRAY_BUFFER: int = 0
    SSBO: int = 1
    INDEX_BUFFER: int = 2


class BufferObject:
    def __init__(
        self,
        buffer_type: BufferType = BufferType.ARRAY_BUFFER,
        object_size: int = 4,
        render_data_offset: List[int] = [0],
        render_data_size: List[int] = [4],
    ) -> None:
        self.loaded: bool = False
        self.data: np.ndarray | None = None
        self.handle: int = glGenBuffers(1)
        self.location: int = 0
        self.buffer_type: BufferType = buffer_type
        if self.buffer_type == BufferType.SSBO:
            self.size: int = 0
            self.max_ssbo_size: int = glGetIntegerv(GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.object_size: int = object_size
        self.render_data_offset: List[int] = render_data_offset
        self.render_data_size: List[int] = render_data_size

    def load(self, data: np.ndarray) -> None:
        glBindVertexArray(0)

        self.data = data

        self.size = data.nbytes
        if self.buffer_type == BufferType.SSBO:
            if data.nbytes > self.max_ssbo_size:
                raise Exception(
                    "Data to big for SSBO (%d bytes, max %d bytes)."
                    % (data.nbytes, self.max_ssbo_size)
                )

            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle)
            glBufferData(GL_SHADER_STORAGE_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        elif self.buffer_type == BufferType.ARRAY_BUFFER:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle)
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        else:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.handle)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        self.loaded = True

    def read(self) -> np.ndarray:
        target = GL_SHADER_STORAGE_BUFFER
        if self.buffer_type == BufferType.ARRAY_BUFFER:
            target = GL_ARRAY_BUFFER
        elif self.buffer_type == BufferType.INDEX_BUFFER:
            target = GL_ELEMENT_ARRAY_BUFFER

        glBindBuffer(target, self.handle)
        return np.frombuffer(
            glGetBufferSubData(target, 0, self.size),
            dtype=self.data.dtype,
        )

    def bind(self, location: int, rendering: bool = False, divisor: int = 0) -> None:
        if self.buffer_type == BufferType.SSBO:
            if rendering:
                glBindBuffer(GL_ARRAY_BUFFER, self.handle)
                for i in range(len(self.render_data_offset)):
                    glEnableVertexAttribArray(location + i)
                    glVertexAttribPointer(
                        location + i,
                        self.render_data_size[i],
                        GL_FLOAT,
                        GL_FALSE,
                        self.object_size * 4,
                        ctypes.c_void_p(4 * self.render_data_offset[i]),
                    )
                    if divisor > 0:
                        glVertexAttribDivisor(location + i, divisor)
            else:
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, location, self.handle)
        elif self.buffer_type == BufferType.ARRAY_BUFFER:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle)
            for i in range(len(self.render_data_offset)):
                glEnableVertexAttribArray(location + i)
                glVertexAttribPointer(
                    location + i,
                    self.render_data_size[i],
                    GL_FLOAT,
                    GL_FALSE,
                    self.object_size * 4,
                    ctypes.c_void_p(4 * self.render_data_offset[i]),
                )
                if divisor > 0:
                    glVertexAttribDivisor(location + i, divisor)
        elif self.buffer_type == BufferType.INDEX_BUFFER:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.handle)

    def clear(self) -> None:
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.handle)
        glClearBufferData(GL_SHADER_STORAGE_BUFFER, GL_RGBA32F, GL_RGBA, GL_FLOAT, None)

    def delete(self) -> None:
        glDeleteBuffers(1, [self.handle])


class BufferCopy(BufferObject):
    def __init__(
        self,
        buffer: BufferObject,
        buffer_type: BufferType = BufferType.ARRAY_BUFFER,
        object_size: int = 4,
        render_data_offset: List[int] = [0],
        render_data_size: List[int] = [4],
    ) -> None:
        self.buffer = buffer
        self.handle: int = buffer.handle
        self.location: int = 0
        self.buffer_type: BufferType = buffer_type
        if self.buffer_type == BufferType.SSBO:
            self.max_ssbo_size: int = glGetIntegerv(GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.object_size: int = object_size
        self.render_data_offset: List[int] = render_data_offset
        self.render_data_size: List[int] = render_data_size

    @property
    def data(self) -> np.ndarray:
        return self.buffer.data

    @property
    def loaded(self) -> bool:
        return self.buffer.loaded

    @property
    def size(self) -> bool:
        return self.buffer.size

    def delete(self) -> None:
        pass


class SwappingBufferObject(BufferObject):
    def __init__(
        self,
        buffer_type: BufferType = BufferType.ARRAY_BUFFER,
        object_size: int = 4,
        render_data_offset: List[int] = [0],
        render_data_size: List[int] = [4],
    ) -> None:
        super().__init__(buffer_type, object_size, render_data_offset, render_data_size)
        self.swap_handle: int = glGenBuffers(1)

    def swap(self) -> None:
        self.handle, self.swap_handle = self.swap_handle, self.handle

    def load(self, data: np.ndarray) -> None:
        super().load(data)
        self.swap()
        super().load(data)

    def bind(self, location: int, rendering: bool = False, divisor: int = 0) -> None:
        if self.buffer_type == BufferType.SSBO:
            if rendering:
                glBindBuffer(GL_ARRAY_BUFFER, self.handle)
                for i in range(len(self.render_data_offset)):
                    glEnableVertexAttribArray(location + i)
                    glVertexAttribPointer(
                        location + i,
                        self.render_data_size[i],
                        GL_FLOAT,
                        GL_FALSE,
                        self.object_size * 4,
                        ctypes.c_void_p(4 * self.render_data_offset[i]),
                    )
                    if divisor > 0:
                        glVertexAttribDivisor(location + i, divisor)
            else:
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, location, self.handle)
                glBindBufferBase(
                    GL_SHADER_STORAGE_BUFFER, location + 1, self.swap_handle
                )
        elif self.buffer_type == BufferType.ARRAY_BUFFER:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle)
            for i in range(len(self.render_data_offset)):
                glEnableVertexAttribArray(location + i)
                glVertexAttribPointer(
                    location + i,
                    self.render_data_size[i],
                    GL_FLOAT,
                    GL_FALSE,
                    self.object_size * 4,
                    ctypes.c_void_p(4 * self.render_data_offset[i]),
                )
                if divisor > 0:
                    glVertexAttribDivisor(location + i, divisor)
        elif self.buffer_type == BufferType.INDEX_BUFFER:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.handle)

    def delete(self) -> None:
        glDeleteBuffers(1, [self.handle])
        glDeleteBuffers(1, [self.swap_handle])

    def clear(self) -> None:
        super().clear()
        self.swap()
        super().clear()


class OverflowingBufferObject:
    def __init__(
        self,
        data_splitting_function,
        object_size: int = 4,
        render_data_offset: List[int] = [0],
        render_data_size: List[int] = [4],
    ) -> None:
        self.data: np.ndarray | None = None
        self.loaded: bool = False
        self.handle: List[int] = [glGenBuffers(1)]
        self.location: int = 0
        self.overall_size: int = 0
        self.size: List[int] = []
        self.max_ssbo_size: int = glGetIntegerv(GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.max_buffer_objects: int = glGetIntegerv(
            GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS
        )
        self.data_splitting_function: Callable[
            [np.ndarray, int, int, int], np.ndarray
        ] = data_splitting_function
        self.object_size: int = object_size
        self.render_data_offset: List[int] = render_data_offset
        self.render_data_size: List[int] = render_data_size

    def load(self, data: np.ndarray) -> None:
        self.data = data
        glBindVertexArray(0)

        self.overall_size = data.nbytes
        if data.nbytes > self.max_ssbo_size:
            buffer_count = math.ceil(data.nbytes / self.max_ssbo_size)
            for i in range(buffer_count):
                if i >= len(self.handle):
                    self.handle.append(glGenBuffers(1))
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[i])
                split_data = self.data_splitting_function(
                    data, i, self.max_ssbo_size, self.object_size
                )
                self.size.append(split_data.nbytes)
                glBufferData(
                    GL_SHADER_STORAGE_BUFFER,
                    split_data.nbytes,
                    split_data,
                    GL_STATIC_DRAW,
                )
        else:
            if self.size:
                self.size[0] = data.nbytes
            else:
                self.size.append(data.nbytes)
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[0])
            glBufferData(GL_SHADER_STORAGE_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        self.loaded = True

    def load_empty(self, dtype, size: int, component_size: int) -> None:
        glBindVertexArray(0)

        self.overall_size = size * self.object_size * 4
        if self.overall_size > self.max_ssbo_size:
            empty = np.zeros(int(self.max_ssbo_size / 4), dtype=dtype)
            buffer_count = math.ceil(
                int(size / component_size)
                / int(self.max_ssbo_size / (component_size * self.object_size * 4))
            )
            logging.info("Data split into %i buffer" % buffer_count)
            for i in range(buffer_count):
                if i >= len(self.handle):
                    self.handle.append(glGenBuffers(1))
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[i])
                self.size.append(empty.nbytes)
                glBufferData(
                    GL_SHADER_STORAGE_BUFFER, empty.nbytes, empty, GL_STATIC_DRAW
                )
        else:
            empty = np.zeros(size * self.object_size, dtype=dtype)
            self.size.append(empty.nbytes)
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[0])
            glBufferData(GL_SHADER_STORAGE_BUFFER, empty.nbytes, empty, GL_STATIC_DRAW)
        self.loaded = True

    def read(self) -> any:
        data = None
        for i, buffer in enumerate(self.handle):
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, buffer)
            if data is None:
                data = np.frombuffer(
                    glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.size[i]),
                    dtype=self.data.dtype,
                )
            else:
                data = np.concatenate(
                    (
                        data,
                        np.frombuffer(
                            glGetBufferSubData(
                                GL_SHADER_STORAGE_BUFFER, 0, self.size[i]
                            ),
                            dtype=self.data.dtype,
                        ),
                    )
                )
        return data

    def bind_single(
        self, buffer_id: int, location: int, rendering: bool = False, divisor: int = 0
    ) -> None:
        if rendering:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle[buffer_id])
            for i in range(len(self.render_data_offset)):
                glEnableVertexAttribArray(location + i)
                glVertexAttribPointer(
                    location + i,
                    self.render_data_size[i],
                    GL_FLOAT,
                    GL_FALSE,
                    self.object_size * 4,
                    ctypes.c_void_p(4 * self.render_data_offset[i]),
                )
                if divisor > 0:
                    glVertexAttribDivisor(location + i, divisor)
        else:
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER, location, self.handle[buffer_id])

    def bind_consecutive(self, location: int) -> None:
        for i, buffer in enumerate(self.handle):
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER, location + i, buffer)

    def clear(self) -> None:
        self.load_empty(self.data.dtype, len(self.data), self.object_size)

    def delete(self) -> None:
        for buffer in self.handle:
            glDeleteBuffers(1, [buffer])
        self.handle = []

    def get_objects(self, buffer_id: int = 0) -> int:
        return int(self.size[buffer_id] / (self.object_size * 4))
