import abc
import os
from pathlib import Path
from typing import Dict

from ...utility.definitions import SHADER_PATH
from ..base.shader import BaseShader, ShaderSetting
from ..base.shader_parser import ShaderParser, get_shader_src
from .shader import RenderShader, RenderShaderSetting


class BaseShaderHandler:
    def __init__(self) -> None:
        __metaclass__ = abc.ABCMeta
        self.shader_list: Dict[str, BaseShader] = dict()
        self.shader_dir: str = SHADER_PATH
        if not os.path.exists(self.shader_dir):
            self.shader_dir = os.path.join(
                Path(SHADER_PATH).parent.absolute(), "shader"
            )
            if not os.path.exists(self.shader_dir):
                self.shader_dir = SHADER_PATH

    @abc.abstractmethod
    def create(
        self, shader_setting: ShaderSetting, parser: ShaderParser | None = None
    ) -> BaseShader:
        raise NotImplementedError

    def get(self, shader_name: str) -> BaseShader:
        return self.shader_list[shader_name]


class RenderShaderHandler(BaseShaderHandler):
    def create(
        self, shader_setting: ShaderSetting, parser: ShaderParser | None = None
    ) -> RenderShader:
        assert isinstance(shader_setting, RenderShaderSetting)

        if shader_setting.id_name in self.shader_list.keys():
            return self.shader_list[shader_setting.id_name]
        vertex_path: str = os.path.join(self.shader_dir, shader_setting.vertex)
        vertex_src: str = (
            get_shader_src(vertex_path) if parser is None else parser.parse(vertex_path)
        )
        fragment_path: str = os.path.join(self.shader_dir, shader_setting.fragment)
        fragment_src: str = (
            get_shader_src(fragment_path)
            if parser is None
            else parser.parse(fragment_path)
        )
        geometry_src: str | None = None
        if shader_setting.geometry is not None:
            geometry_path: str = os.path.join(self.shader_dir, shader_setting.geometry)
            geometry_src = (
                get_shader_src(geometry_path)
                if parser is None
                else parser.parse(geometry_path)
            )
        self.shader_list[shader_setting.id_name] = RenderShader(
            vertex_src, fragment_src, geometry_src, shader_setting.uniform_labels
        )
        return self.shader_list[shader_setting.id_name]
