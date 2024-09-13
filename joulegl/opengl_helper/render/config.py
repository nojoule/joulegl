from typing import Any, List, Tuple

from opengl_helper.base.config import ShaderConfig


class RenderConfig(ShaderConfig):
    def __init__(self, name: str | None = None) -> None:
        super().__init__("rendering", name)

    def set_defaults(self) -> None:
        shader_items: List[Tuple[str, str, str, Any]] = []
        shader_items.extend(
            [
                ("screen_width", "screen_width", "Screen Width", 1920.0),
                ("screen_height", "screen_height", "Screen Height", 1080.0),
            ]
        )

        selection_items: List[Tuple[str, List[str], List[Any], int]] = []
        selection_items.extend([])
        self.set_items(shader_items, selection_items)
