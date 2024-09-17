import os
import time

import numpy as np
from OpenGL.GL import *

from joulegl.utility.performance import Timed

from ..opengl_helper.render.utility import clear_screen
from ..opengl_helper.screenshot import create_screenshot
from .camera import CameraPose
from .file import StatsFileHandler
from .log_handling import LOGGER
from .window import Window, WindowHandler


class App(Timed):
    def __init__(self, app_name: str = "JouleGL", hidden: bool = False) -> None:
        super().__init__()
        self.title: str = app_name
        self.name = app_name.lower().replace(" ", "-")
        StatsFileHandler().load_statistics(app_name=self.name)

        self.window_handler: WindowHandler = WindowHandler()
        self.window: Window = self.window_handler.create_window(
            self.name, hidden=hidden, title=self.title
        )
        self.window.set_callbacks(self.key_input, self.mouse_input)
        self.window.activate()
        LOGGER.info(
            f"OpenGL Version: {glGetIntegerv(GL_MAJOR_VERSION)}.{glGetIntegerv(GL_MINOR_VERSION)}"
        )

        self.closed: bool = False

    def key_input(self, key, scancode, action, mods) -> bool:  # pragma: no cover
        return False

    def mouse_input(self, button, action, mods) -> bool:  # pragma: no cover
        return False

    def render(self) -> None:  # pragma: no cover
        pass

    def setup(self) -> None:  # pragma: no cover
        pass

    def frame(self) -> None:
        assert self.window is not None
        self.window_handler.update()
        clear_screen([1.0, 1.0, 1.0, 1.0])
        self.render()
        self.window.swap()

    def set_cam(
        self,
        base: np.ndarray = np.array([0.0, 0.0, 0.0]),
        offset_scale: float = 1.0,
        pose: CameraPose = CameraPose.LEFT,
    ) -> None:
        assert self.window is not None
        self.window.cam.update_base(base)
        self.window.cam.offset_scale = offset_scale
        self.window.cam.set_position(pose)

    def run(self) -> None:
        try:
            while self.window.is_active() and not self.closed:
                self.frame()

                if self.window.screenshot:
                    width, height = self.window.get_size()
                    create_screenshot(int(width), int(height))
                    self.window.screenshot = False
                elif self.window.record:
                    width, height = self.window.get_size()
                    self.window.frame_id += 1
                    create_screenshot(
                        int(width), int(height), frame_id=self.window.frame_id
                    )

                pause_for = self.check_time()
                if pause_for > 0:
                    time.sleep(pause_for / 1000.0)
        except KeyboardInterrupt:
            pass
        self.cleanup()

    def close(self) -> None:
        self.closed = True

    def cleanup(self) -> None:
        StatsFileHandler(data_path=os.getcwd()).write_statistics(app_name=self.name)
        self.window_handler.close(self.window)
