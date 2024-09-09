from enum import Enum
from typing import Dict, List, Tuple

from ...utility.config import BaseConfig


class ShaderConfigType(Enum):
    GENERAL = 1
    SHADER = 2
    SELECTION = 3


class ShaderConfig(BaseConfig):
    def __init__(self, type_name: str | None = None, name: str | None = None) -> None:
        if type_name is None:
            type_name = "shader"
        if name is None:
            super().__init__(type_name)
        else:
            super().__init__(type_name, name)

        self.shader_label: Dict[str, str] = dict()
        self.shader_name: Dict[str, str] = dict()
        self.selection_labels: Dict[str, List[str]] = dict()
        self.selection_values: Dict[str, List[any]] = dict()
        self.item_type: Dict[str, ShaderConfigType] = dict()
        self.set_defaults()

    def set_items(
        self,
        shader_items: List[Tuple[str, str, str, any]],
        selection_items: List[Tuple[str, List[str], List[any], int]] | None = None,
    ) -> None:
        for key, shader_name, label, value in shader_items:
            self.shader_label[key] = label
            self.shader_name[key] = shader_name
            self.item_type[key] = ShaderConfigType.SHADER
            self.setdefault(key, value)

        for key, labels, values, default in selection_items:
            self.selection_labels[key] = labels
            self.selection_values[key] = values
            self.item_type[key] = ShaderConfigType.SELECTION
            self.setdefault(key, default)

    def set_defaults(self) -> None:
        shader_items: List[Tuple[str, str, str, any]] = []
        shader_items.extend(
            [
                ("screen_width", "screen_width", "Screen Width", 1920.0),
                ("screen_height", "screen_height", "Screen Height", 1080.0),
            ]
        )

        selection_items: List[Tuple[str, List[str], List[any], int]] = []
        selection_items.extend([])
        self.set_items(shader_items, selection_items)
