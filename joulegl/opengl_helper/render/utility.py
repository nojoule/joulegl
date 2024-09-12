from enum import Enum
from typing import Any, Callable, List, Union

from OpenGL.GL import *


def clear_screen(clear_color: List[float]) -> None:
    glClearColor(clear_color[0], clear_color[1], clear_color[2], clear_color[3])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


class OGLRenderFunction(Enum):
    ARRAYS = 1
    ARRAYS_INSTANCED = 2
    ELEMENTS = 3


def generate_render_function(
    ogl_func: OGLRenderFunction,
    primitive: Any,
    point_size: float | None = None,
    line_width: float | None = None,
    add_blending: bool = False,
    depth_test: bool = False,
    instance_vertices: int = 1,
) -> Callable:
    ogl_func: OGLRenderFunction = ogl_func
    primitive: Any = primitive
    point_size: float = point_size
    line_width: float = line_width
    add_blending: bool = add_blending
    depth_test: bool = depth_test
    instance_vertices: int = instance_vertices

    def render_func(element_count: int, _=None) -> None:
        if add_blending:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBlendEquationSeparate(GL_MIN, GL_MAX)
        else:
            glDisable(GL_BLEND)
        if depth_test:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

        if point_size is not None:
            glPointSize(point_size)

        if line_width is not None:
            glLineWidth(line_width)

        if ogl_func is OGLRenderFunction.ARRAYS:
            glDrawArrays(primitive, 0, element_count)
        elif ogl_func is OGLRenderFunction.ARRAYS_INSTANCED:
            glDrawArraysInstanced(primitive, 0, instance_vertices, element_count)
        elif ogl_func is OGLRenderFunction.ELEMENTS:
            glDrawElements(primitive, element_count, GL_UNSIGNED_INT, None)

        glMemoryBarrier(GL_ALL_BARRIER_BITS)

    return render_func
