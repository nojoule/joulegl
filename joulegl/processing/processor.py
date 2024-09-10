import abc

from ..opengl_helper.base.config import ShaderConfig
from ..opengl_helper.base.shader_parser import ShaderParser
from ..opengl_helper.compute.shader_handler import ComputeShaderHandler
from ..rendering.renderer import BaseProcessor


class ComputeProcessor(BaseProcessor):
    def __init__(self, shader_parser: ShaderParser | None = None) -> None:
        super().__init__(ComputeShaderHandler(), shader_parser)
        __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self, set_name: str, config: ShaderConfig | None = None) -> None:
        raise NotImplementedError
