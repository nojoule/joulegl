from typing import List

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from ..base.shader import BaseShader, ShaderSetting


class RenderShaderSetting(ShaderSetting):
    def __init__(
        self,
        id_name: str,
        shader_paths: List[str],
        uniform_labels: List[str] | None = None,
    ) -> None:
        super().__init__(id_name, uniform_labels)
        if len(shader_paths) < 2 or len(shader_paths) > 3:
            raise Exception(
                "Can't handle number of shaders for a program (either 2 or 3 with geometry shader)."
            )
        self.vertex: str = shader_paths[0]
        self.fragment: str = shader_paths[1]
        self.geometry: str = None if len(shader_paths) < 3 else shader_paths[2]


class RenderShader(BaseShader):
    def __init__(
        self,
        name: str,
        vertex_src: str,
        fragment_src: str,
        geometry_src: str | None = None,
        uniform_labels: List[str] = [],
    ) -> None:
        BaseShader.__init__(self, name)
        if geometry_src is None:
            self.shader_handle = compileProgram(
                compileShader(vertex_src, GL_VERTEX_SHADER),
                compileShader(fragment_src, GL_FRAGMENT_SHADER),
            )
        else:
            self.shader_handle = compileProgram(
                compileShader(vertex_src, GL_VERTEX_SHADER),
                compileShader(fragment_src, GL_FRAGMENT_SHADER),
                compileShader(geometry_src, GL_GEOMETRY_SHADER),
            )
        self.set_uniform_label(uniform_labels)

    def use(self) -> None:
        for texture, _, texture_position in self.textures:
            texture.bind_as_texture(texture_position)
        glUseProgram(self.shader_handle)

        for (
            uniform_location,
            uniform_data,
            uniform_setter,
        ) in self.uniform_cache.values():
            uniform_setter(uniform_location, uniform_data)
