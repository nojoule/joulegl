from enum import Enum
from typing import Any, Callable, List, Tuple, Union

from OpenGL.GL import *


def clear_screen(clear_color: List[float]) -> None:
    glClearColor(clear_color[0], clear_color[1], clear_color[2], clear_color[3])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


class OGLRenderFunction(Enum):
    ARRAYS = 1
    ARRAYS_INSTANCED = 2
    ELEMENTS = 3


class OglPrimitives(Enum):
    POINTS = 0
    LINE_STRIP = 1
    LINE_LOOP = 2
    LINES = 3
    LINE_STRIP_ADJACENCY = 4
    LINES_ADJACENCY = 5
    TRIANGLE_STRIP = 6
    TRIANGLE_FAN = 7
    TRIANGLES = 8
    TRIANGLE_STRIP_ADJACENCY = 9
    TRIANGLES_ADJACENCY = 10


OGL_PRIMITVE_MAP = {
    OglPrimitives.POINTS: GL_POINTS,
    OglPrimitives.LINE_STRIP: GL_LINE_STRIP,
    OglPrimitives.LINE_LOOP: GL_LINE_LOOP,
    OglPrimitives.LINES: GL_LINES,
    OglPrimitives.LINE_STRIP_ADJACENCY: GL_LINE_STRIP_ADJACENCY,
    OglPrimitives.LINES_ADJACENCY: GL_LINES_ADJACENCY,
    OglPrimitives.TRIANGLE_STRIP: GL_TRIANGLE_STRIP,
    OglPrimitives.TRIANGLE_FAN: GL_TRIANGLE_FAN,
    OglPrimitives.TRIANGLES: GL_TRIANGLES,
    OglPrimitives.TRIANGLE_STRIP_ADJACENCY: GL_TRIANGLE_STRIP_ADJACENCY,
    OglPrimitives.TRIANGLES_ADJACENCY: GL_TRIANGLES_ADJACENCY,
}


class OglBlendingFactors(Enum):
    ZERO = 0
    ONE = 1
    SRC_COLOR = 2
    ONE_MINUS_SRC_COLOR = 3
    DST_COLOR = 4
    ONE_MINUS_DST_COLOR = 5
    SRC_ALPHA = 6
    ONE_MINUS_SRC_ALPHA = 7
    DST_ALPHA = 8
    ONE_MINUS_DST_ALPHA = 9
    CONSTANT_COLOR = 10
    ONE_MINUS_CONSTANT_COLOR = 11
    CONSTANT_ALPHA = 12
    ONE_MINUS_CONSTANT_ALPHA = 13


OGL_BLENDING_FACTOR_MAP = {
    OglBlendingFactors.ZERO: GL_ZERO,
    OglBlendingFactors.ONE: GL_ONE,
    OglBlendingFactors.SRC_COLOR: GL_SRC_COLOR,
    OglBlendingFactors.ONE_MINUS_SRC_COLOR: GL_ONE_MINUS_SRC_COLOR,
    OglBlendingFactors.DST_COLOR: GL_DST_COLOR,
    OglBlendingFactors.ONE_MINUS_DST_COLOR: GL_ONE_MINUS_DST_COLOR,
    OglBlendingFactors.SRC_ALPHA: GL_SRC_ALPHA,
    OglBlendingFactors.ONE_MINUS_SRC_ALPHA: GL_ONE_MINUS_SRC_ALPHA,
    OglBlendingFactors.DST_ALPHA: GL_DST_ALPHA,
    OglBlendingFactors.ONE_MINUS_DST_ALPHA: GL_ONE_MINUS_DST_ALPHA,
    OglBlendingFactors.CONSTANT_COLOR: GL_CONSTANT_COLOR,
    OglBlendingFactors.ONE_MINUS_CONSTANT_COLOR: GL_ONE_MINUS_CONSTANT_COLOR,
    OglBlendingFactors.CONSTANT_ALPHA: GL_CONSTANT_ALPHA,
    OglBlendingFactors.ONE_MINUS_CONSTANT_ALPHA: GL_ONE_MINUS_CONSTANT_ALPHA,
}


class OglBlendingEquations(Enum):
    FUNC_ADD = 0
    FUNC_SUBTRACT = 1
    FUNC_REVERSE_SUBTRACT = 2
    MIN = 3
    MAX = 4


OGL_BLENDING_EQUATION_MAP = {
    OglBlendingEquations.FUNC_ADD: GL_FUNC_ADD,
    OglBlendingEquations.FUNC_SUBTRACT: GL_FUNC_SUBTRACT,
    OglBlendingEquations.FUNC_REVERSE_SUBTRACT: GL_FUNC_REVERSE_SUBTRACT,
    OglBlendingEquations.MIN: GL_MIN,
    OglBlendingEquations.MAX: GL_MAX,
}


def generate_render_function(
    ogl_func: OGLRenderFunction,
    primitive: OglPrimitives,
    point_size: float | None = None,
    line_width: float | None = None,
    add_blending: (
        None
        | Tuple[
            OglBlendingFactors,
            OglBlendingFactors,
            OglBlendingEquations,
            OglBlendingEquations,
        ]
    ) = None,
    depth_test: bool = False,
    instance_vertices: int = 1,
) -> Callable:
    ogl_func: OGLRenderFunction = ogl_func
    primitive: OglPrimitives = primitive
    point_size: float = point_size
    line_width: float = line_width
    add_blending: bool = add_blending
    depth_test: bool = depth_test
    instance_vertices: int = instance_vertices

    def render_func(element_count: int, _=None) -> None:
        if add_blending is not None:
            glEnable(GL_BLEND)
            glBlendFunc(
                OGL_BLENDING_FACTOR_MAP[add_blending[0]],
                OGL_BLENDING_FACTOR_MAP[add_blending[1]],
            )
            glBlendEquationSeparate(
                OGL_BLENDING_EQUATION_MAP[add_blending[2]],
                OGL_BLENDING_EQUATION_MAP[add_blending[3]],
            )
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
            glDrawArrays(OGL_PRIMITVE_MAP[primitive], 0, element_count)
        elif ogl_func is OGLRenderFunction.ARRAYS_INSTANCED:
            glDrawArraysInstanced(
                OGL_PRIMITVE_MAP[primitive], 0, instance_vertices, element_count
            )
        elif ogl_func is OGLRenderFunction.ELEMENTS:
            glDrawElements(
                OGL_PRIMITVE_MAP[primitive], element_count, GL_UNSIGNED_INT, None
            )

        glMemoryBarrier(GL_ALL_BARRIER_BITS)

    return render_func
