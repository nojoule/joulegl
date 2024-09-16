import os

from ..base.shader import ShaderSetting
from ..base.shader_parser import ShaderParser, get_shader_src
from ..compute.shader import ComputeShader, ComputeShaderSetting
from ..render.shader_handler import BaseShaderHandler


class ComputeShaderHandler(BaseShaderHandler):
    def create(
        self, shader_setting: ShaderSetting, parser: ShaderParser | None = None
    ) -> ComputeShader:
        if not isinstance(shader_setting, ComputeShaderSetting):
            raise ValueError("ComputeShaderSetting required for ComputeShaderHandler")
        if shader_setting.id_name in self.shader_list.keys():
            return self.shader_list[shader_setting.id_name]
        shader_path: str = os.path.join(self.shader_dir, shader_setting.src)
        shader_src = (
            get_shader_src(shader_path) if parser is None else parser.parse(shader_path)
        )
        self.shader_list[shader_setting.id_name] = ComputeShader(
            shader_setting.id_name, shader_src
        )
        return self.shader_list[shader_setting.id_name]
