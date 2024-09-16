from typing import Any, List, Tuple

from opengl_helper.base.config import ShaderConfig


class RenderConfig(ShaderConfig):
    def __init__(self, name: str | None = None) -> None:
        super().__init__("rendering", name)
