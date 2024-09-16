from enum import Enum
from typing import Any, Dict, List, Tuple

from ...utility.config import BaseConfig


class ShaderConfig(BaseConfig):
    def __init__(self, type_name: str | None = None, name: str | None = None) -> None:
        if type_name is None:
            type_name = "shader"
        if name is None:
            super().__init__(type_name)
        else:
            super().__init__(type_name, name)

        self.shader_name: Dict[str, str] = dict()
        self.shader_uniform_name_map: Dict[str, List[str]] = dict()
        self.uniform_type: Dict[str, str] = dict()

    def set_items(self, shader_items: List[Tuple[str, List[str], str, Any]]) -> None:
        for key, shader_names, uniform_type, value in shader_items:
            for shader_name in shader_names:
                if shader_name in self.shader_uniform_name_map:
                    self.shader_uniform_name_map[shader_name].append(key)
                else:
                    self.shader_uniform_name_map[shader_name] = [key]

            self.shader_name[key] = (
                shader_names
                if key not in self.shader_name
                else self.shader_name[key] + shader_names
            )
            self.uniform_type[key] = uniform_type
            self.setdefault(key, value)
