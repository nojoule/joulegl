import abc
from typing import Any, Callable, Dict, List, Tuple

from OpenGL.GL import *

from ..texture import Texture
from .config import ShaderConfig


def uniform_setter_function(uniform_setter: str) -> Callable:
    if uniform_setter == "float":

        def uniform_func(location: int, data: float) -> None:
            glUniform1f(location, data)

        return uniform_func
    elif uniform_setter == "vec3":

        def uniform_func(location: int, data: List[float]) -> None:
            glUniform3fv(location, 1, data)

        return uniform_func
    elif uniform_setter == "mat4":

        def uniform_func(location: int, data: List[float]) -> None:
            glUniformMatrix4fv(location, 1, GL_FALSE, data)

        return uniform_func
    elif uniform_setter == "int":

        def uniform_func(location: int, data: int) -> None:
            glUniform1i(location, data)

        return uniform_func
    elif uniform_setter == "ivec3":

        def uniform_func(location: int, data: List[int]) -> None:
            glUniform3iv(location, 1, data)

        return uniform_func
    raise Exception("Uniform setter function for '%s' not defined." % uniform_setter)


class ShaderSetting:
    def __init__(self, id_name: str, uniform_labels: List[str] | None = None) -> None:
        self.id_name: str = id_name
        self.uniform_labels: List[str] = (
            uniform_labels if uniform_labels is not None else []
        )


class BaseShader:
    def __init__(self, name: str) -> None:
        __metaclass__ = abc.ABCMeta
        self.name: str = name
        self.shader_handle: int = 0
        self.textures: List[Tuple[Texture, str, int]] = []
        self.uniform_cache: Dict[str, Tuple[int, Any, Callable]] = dict()
        self.uniform_labels: List[str] = []
        self.uniform_ignore_labels: List[str] = []

    def set_uniform_label(self, data: List[str]) -> None:
        for setting in data:
            self.uniform_labels.append(setting)

    def set_uniform_labeled_data(self, config: ShaderConfig | None) -> None:
        if config is not None:
            uniform_data = []
            if self.name in config.shader_uniform_name_map:
                uniform_names = config.shader_uniform_name_map[self.name]
                for uniform_name in uniform_names:
                    if uniform_name in self.uniform_labels:
                        uniform_data.append(
                            (
                                uniform_name,
                                config[uniform_name],
                                config.uniform_type[uniform_name],
                            )
                        )
            self.set_uniform_data(uniform_data)

    def set_uniform_data(self, data: List[Tuple[str, Any, str]]) -> None:
        program_is_set: bool = False
        for uniform_name, uniform_data, uniform_setter in data:
            if uniform_name not in self.uniform_ignore_labels:
                if uniform_name not in self.uniform_cache.keys():
                    if not program_is_set:
                        glUseProgram(self.shader_handle)
                        program_is_set = True
                    uniform_location = glGetUniformLocation(
                        self.shader_handle, uniform_name
                    )
                    if uniform_location != -1:
                        self.uniform_cache[uniform_name] = (
                            uniform_location,
                            uniform_data,
                            uniform_setter_function(uniform_setter),
                        )
                    else:
                        self.uniform_ignore_labels.append(uniform_name)
                else:
                    uniform_location, _, setter = self.uniform_cache[uniform_name]
                    self.uniform_cache[uniform_name] = (
                        uniform_location,
                        uniform_data,
                        setter,
                    )

    def set_textures(self, textures: List[Tuple[Texture, str, int]]) -> None:
        self.textures: List[Tuple[Texture, str, int]] = textures

    @abc.abstractmethod
    def use(self) -> None:
        raise NotImplementedError
