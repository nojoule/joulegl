import math
from typing import Any, Dict, List, Tuple

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from ..render.shader import BaseShader, ShaderSetting
from ..texture import Texture


class ComputeShaderSetting(ShaderSetting):
    def __init__(
        self,
        id_name: str,
        shader_paths: List[str],
        uniform_labels: List[str] | None = None,
    ) -> None:
        super().__init__(id_name, uniform_labels)
        if len(shader_paths) != 1:
            raise Exception("Can't handle number of shaders for a program (must be 1).")
        self.src: str = shader_paths[0]


class ComputeShader(BaseShader):
    def __init__(self, name: str, shader_src: str) -> None:
        BaseShader.__init__(self, name)
        self.shader_handle: int = compileProgram(
            compileShader(shader_src, GL_COMPUTE_SHADER)
        )
        self.textures: List[Tuple[Texture, str, int]] = []
        self.uniform_cache: Dict[str, Tuple[int, Any, Any]] = dict()
        self.max_workgroup_size: int = glGetIntegeri_v(
            GL_MAX_COMPUTE_WORK_GROUP_COUNT, 0
        )[0]

    def compute(self, width: int, barrier: bool = False) -> None:
        for i in range(math.ceil(width / self.max_workgroup_size)):
            self.set_uniform_data(
                [("work_group_offset", i * self.max_workgroup_size, "int")]
            )

            for (
                uniform_location,
                uniform_data,
                uniform_setter,
            ) in self.uniform_cache.values():
                uniform_setter(uniform_location, uniform_data)

            if i == math.ceil(width / self.max_workgroup_size) - 1:
                glDispatchCompute(width % self.max_workgroup_size, 1, 1)
            else:
                glDispatchCompute(self.max_workgroup_size, 1, 1)
        if barrier:
            self.barrier()

    @staticmethod
    def barrier() -> None:
        glMemoryBarrier(GL_ALL_BARRIER_BITS)

    def use(self) -> None:
        for texture, flag, image_position in self.textures:
            texture.bind_as_image(flag, image_position)
        glUseProgram(self.shader_handle)
