import abc
from typing import List, Tuple

from OpenGL.GL import *

from .buffer import BufferObject, OverflowingBufferObject


class BaseDataHandler:
    def __init__(self) -> None:
        __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set(self, rendering: bool = False) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self) -> None:
        raise NotImplementedError


class VertexDataHandler(BaseDataHandler):
    def __init__(
        self,
        targeted_buffer_objects: List[Tuple[BufferObject, int]],
        buffer_divisor: List[Tuple[int, int]] = [],
        untargeted_buffer_objects: List[BufferObject] = [],
    ) -> None:
        super().__init__()
        self.handle: int = glGenVertexArrays(1)
        self.targeted_buffer_objects: List[Tuple[BufferObject, int]] = (
            targeted_buffer_objects
        )
        self.untargeted_buffer_objects: List[BufferObject] = untargeted_buffer_objects
        self.buffer_divisor: List[Tuple[int, int]] = buffer_divisor

    def set(self, rendering: bool = False) -> None:
        glMemoryBarrier(GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT)
        glBindVertexArray(self.handle)
        for i, (buffer, location) in enumerate(self.targeted_buffer_objects):
            if not buffer.loaded:
                raise AssertionError("Buffer was not initalized with data!")
            found_divisor: bool = False
            for buffer_id, divisor in self.buffer_divisor:
                if buffer_id == i:
                    found_divisor = True
                    buffer.bind(location, rendering, divisor=divisor)
            if not found_divisor:
                if len(self.buffer_divisor) == 0:
                    buffer.bind(location, rendering)
                else:
                    buffer.bind(location, rendering, divisor=1)
        for buffer in self.untargeted_buffer_objects:
            if not buffer.loaded:
                raise AssertionError("Buffer was not initalized with data!")
            buffer.bind(0, rendering)

    def delete(self) -> None:
        glDeleteVertexArrays(1, [self.handle])


class OverflowingVertexDataHandler(VertexDataHandler):
    def __init__(
        self,
        targeted_buffer_objects: List[Tuple[BufferObject, int]],
        targeted_overflowing_buffer_objects: List[
            Tuple[OverflowingBufferObject, int]
        ] = [],
        buffer_divisor: List[Tuple[int, int]] = [],
    ) -> None:
        super().__init__(targeted_buffer_objects, buffer_divisor)
        self.targeted_overflowing_buffer_objects: List[
            Tuple[OverflowingBufferObject, int]
        ] = targeted_overflowing_buffer_objects
        self.current_buffer_id: int = 0

    def set_buffer(self, buffer_id: int) -> None:
        self.current_buffer_id = buffer_id

    def set(self, rendering: bool = False) -> None:
        VertexDataHandler.set(self, rendering)
        for buffer, location in self.targeted_overflowing_buffer_objects:
            buffer.bind_single(self.current_buffer_id, location, rendering)

    def set_range(self, count: int) -> None:
        glMemoryBarrier(GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT)
        glBindVertexArray(self.handle)
        for buffer, location in self.targeted_buffer_objects:
            if not buffer.loaded:
                raise AssertionError("Buffer was not initalized with data!")
            buffer.bind(location)
        for buffer, location in self.targeted_overflowing_buffer_objects:
            if not buffer.loaded:
                raise AssertionError("Buffer was not initalized with data!")
            for i in range(count):
                buffer.bind_single(
                    (self.current_buffer_id + i) % len(buffer.overflowing_handles),
                    location + i,
                )

    def set_consecutive(self) -> None:
        glMemoryBarrier(GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT)
        glBindVertexArray(self.handle)
        for buffer, location in self.targeted_buffer_objects:
            buffer.bind(location)
        for buffer, location in self.targeted_overflowing_buffer_objects:
            buffer.bind_consecutive(location)
