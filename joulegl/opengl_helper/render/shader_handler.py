import os

from joulegl.opengl_helper.base.shader_handler import BaseShaderHandler

from ..base.shader import ShaderSetting
from ..base.shader_parser import ShaderParser, get_shader_src
from .shader import RenderShader, RenderShaderSetting


class RenderShaderHandler(BaseShaderHandler):
    def create(
        self, shader_setting: ShaderSetting, parser: ShaderParser | None = None
    ) -> RenderShader:
        if not isinstance(shader_setting, RenderShaderSetting):
            raise ValueError("RenderShaderSetting required for RenderShaderHandler")
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
            shader_setting.id_name,
            vertex_src,
            fragment_src,
            geometry_src,
            shader_setting.uniform_labels,
        )
        return self.shader_list[shader_setting.id_name]
