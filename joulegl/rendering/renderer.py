import abc
from typing import Callable, Dict, List, Tuple

from ..opengl_helper.base.config import ShaderConfig
from ..opengl_helper.base.data_set import DATA_TO_SET_MAP, BaseShaderSet
from ..opengl_helper.base.shader import ShaderSetting
from ..opengl_helper.base.shader_parser import ShaderParser
from ..opengl_helper.render.shader import RenderShader, RenderShaderSetting
from ..opengl_helper.render.shader_handler import BaseShaderHandler, RenderShaderHandler
from ..opengl_helper.vertex_data_handler import BaseDataHandler
from ..utility.camera import Camera


class BaseProcessor:
    def __init__(
        self,
        shader_handler: BaseShaderHandler,
        shader_parser: ShaderParser | None = None,
    ) -> None:
        __metaclass__ = abc.ABCMeta
        self.shader_handler: BaseShaderHandler = shader_handler
        self.shader_parser = shader_parser
        self.shaders: Dict[str, RenderShader] = dict()
        self.sets: Dict[str, BaseShaderSet] = dict()
        self.execute_funcs: Dict[str, Callable] = dict()
        self.element_count_funcs: Dict[str, Callable] = dict()

    def set_shader(self, shader_settings: List[ShaderSetting]) -> None:
        for shader_setting in shader_settings:
            self.shaders[shader_setting.id_name] = self.shader_handler.create(
                shader_setting, self.shader_parser
            )

    def create_set(
        self,
        data_handler: BaseDataHandler,
        name: str,
        shader_func_map: Dict[str, Tuple[str, str]],
    ) -> None:
        for shader_name, (func_name, count_func_name) in shader_func_map.items():
            self.sets[name] = DATA_TO_SET_MAP[type(data_handler)](
                self.shaders[shader_name],
                data_handler,
                self.execute_funcs[func_name],
                self.element_count_funcs[count_func_name],
            )

    def create_sets(self, data_handler: BaseDataHandler) -> None:
        for name, shader in self.shaders.items():
            self.sets[name] = DATA_TO_SET_MAP[type(data_handler)](
                shader,
                data_handler,
                self.execute_funcs[name],
                self.element_count_funcs[name],
            )

    @abc.abstractmethod
    def delete(self) -> None:
        return


class Renderer(BaseProcessor):
    def __init__(self, shader_parser: ShaderParser | None = None) -> None:
        super().__init__(RenderShaderHandler(), shader_parser)
        __metaclass__ = abc.ABCMeta

    def set_shader(self, shader_settings: List[RenderShaderSetting]) -> None:
        for shader_setting in shader_settings:
            self.shaders[shader_setting.id_name] = self.shader_handler.create(
                shader_setting, self.shader_parser
            )

    @abc.abstractmethod
    def render(
        self, set_name: str, cam: Camera, config: ShaderConfig | None = None
    ) -> None:
        return
