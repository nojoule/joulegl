import abc
import os
from pathlib import Path
from typing import Dict

from ...utility.definitions import SHADER_PATH
from ..base.shader import BaseShader, ShaderSetting
from ..base.shader_parser import ShaderParser


class BaseShaderHandler:
    def __init__(self, shader_dir: str = SHADER_PATH) -> None:
        __metaclass__ = abc.ABCMeta
        self.shader_list: Dict[str, BaseShader] = dict()
        self.shader_dir: str = shader_dir
        if not os.path.exists(self.shader_dir):
            self.shader_dir = os.path.join(Path(shader_dir).parent.absolute(), "shader")
            if not os.path.exists(self.shader_dir):
                self.shader_dir = shader_dir

    @abc.abstractmethod
    def create(
        self, shader_setting: ShaderSetting, parser: ShaderParser | None = None
    ) -> BaseShader:
        raise NotImplementedError

    def get(self, shader_name: str) -> BaseShader:
        return self.shader_list[shader_name]
