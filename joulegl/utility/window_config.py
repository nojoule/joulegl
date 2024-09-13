from typing import Any, List, Tuple

from .config import BaseConfig


class WindowConfig(BaseConfig):
    def __init__(self, name: str | None = None, title: str = "JouleGL") -> None:
        self.title = title
        if name is None:
            super().__init__("window")
        else:
            super().__init__("window", name)

        self.set_defaults()

    def set_defaults(self) -> None:
        render_setting_items: List[Tuple[str, Any]] = []
        render_setting_items.extend(
            [
                ("title", self.title),
                ("width", 1600),
                ("height", 900),
                ("screen_width", 1920),
                ("screen_height", 1080),
                ("screen_x", 0),
                ("screen_y", 0),
                ("monitor_id", None),
                ("camera_rotation", False),
                ("camera_rotation_speed", 0.5),
            ]
        )

        for key, value in render_setting_items:
            self.setdefault(key, value)
        self.store()
