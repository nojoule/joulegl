import logging
import math
from enum import Enum
from typing import Callable, List, Tuple

import numpy as np
from OpenGL.GL import *


class BufferType(Enum):
    ARRAY_BUFFER: int = 0
    SHADER_STORAGE_BUFFER: int = 1
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
        self.buffer_type: BufferType = buffer_type
        if self.buffer_type == BufferType.SHADER_STORAGE_BUFFER:
            self.size: int = 0
            self.max_ssbo_size: int = glGetIntegerv(GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.object_size: int = object_size
        self.render_data_offset: List[int] = render_data_offset
        self.render_data_size: List[int] = render_data_size

    def load(self, data: np.ndarray) -> None:
        glBindVertexArray(0)

        self.data = data

        self.size = data.nbytes
        if self.buffer_type == BufferType.SHADER_STORAGE_BUFFER:
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
        if self.buffer_type == BufferType.SHADER_STORAGE_BUFFER:
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
        else:
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
        self.buffer_type: BufferType = buffer_type
        if self.buffer_type == BufferType.SHADER_STORAGE_BUFFER:
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
        if rendering:
            super().bind(location, True, divisor)
        else:
            super().bind(location, False, divisor)
            self.swap()
            super().bind(location + 1, False, divisor)
            self.swap()

    def delete(self) -> None:
        glDeleteBuffers(1, [self.handle])
        glDeleteBuffers(1, [self.swap_handle])

    def clear(self) -> None:
        super().clear()
        self.swap()
        super().clear()


class OverflowingBufferObject(BufferObject):
    def __init__(
        self,
        data_splitting_function,
        object_size: int = 4,
        render_data_offset: List[int] = [0],
        render_data_size: List[int] = [4],
    ) -> None:
        super().__init__(
            BufferType.SHADER_STORAGE_BUFFER,
            object_size,
            render_data_offset,
            render_data_size,
        )
        self.overflowing_handles: List[int] = [self.handle]
        self.overall_size: int = 0
        self.overflowing_sizes: List[int] = []
        self.max_ssbo_size: int = glGetIntegerv(GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.max_buffer_objects: int = glGetIntegerv(
            GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS
        )
        self.data_splitting_function: Callable[
            [np.ndarray, int, int, int], np.ndarray
        ] = data_splitting_function

    def load(self, data: np.ndarray) -> None:
        self.overall_size = data.nbytes
        self.overflowing_sizes = []
        if data.nbytes > self.max_ssbo_size:
            buffer_count = math.ceil(data.nbytes / self.max_ssbo_size)
            for i in range(buffer_count):
                if i >= len(self.overflowing_handles):
                    self.overflowing_handles.append(glGenBuffers(1))

                split_data = self.data_splitting_function(
                    data, i, self.max_ssbo_size, self.object_size
                )
                self.overflowing_sizes.append(split_data.nbytes)

                self.handle = self.overflowing_handles[i]
                self.size = self.overflowing_sizes[i]
                super().load(split_data)
        else:
            self.overflowing_sizes.append(data.nbytes)
            super().load(data)
        self.data = data
        self.loaded = True

    def load_empty(self, dtype, size: int) -> None:
        empty = np.zeros(size, dtype=dtype)
        self.load(empty)

    def read(self) -> np.ndarray:
        data = np.array([], dtype=self.data.dtype)
        for i, handle in enumerate(self.overflowing_handles):
            self.handle = handle
            self.size = self.overflowing_sizes[i]
            split_data = super().read()
            data = np.concatenate([data, split_data])
        return data

    def bind_single(
        self, buffer_id: int, location: int, rendering: bool = False, divisor: int = 0
    ) -> None:
        self.handle = self.overflowing_handles[buffer_id]
        self.size = self.overflowing_sizes[buffer_id]
        self.bind(location, rendering, divisor)

    def bind_consecutive(self, location: int) -> None:
        for i, handle in enumerate(self.overflowing_handles):
            self.handle = handle
            self.size = self.overflowing_sizes[i]
            self.bind(location + i)

    def clear(self) -> None:
        self.load_empty(self.data.dtype, len(self.data))

    def delete(self) -> None:
        for handle in self.overflowing_handles:
            glDeleteBuffers(1, [handle])

    def get_objects(self, buffer_id: int = 0) -> int:
        return int(self.overflowing_sizes[buffer_id] / (self.object_size * 4))
