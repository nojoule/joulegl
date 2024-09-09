import os
import time

import numpy as np
from OpenGL.GL import *

from ..opengl_helper.render.utility import clear_screen
from ..opengl_helper.screenshot import create_screenshot
from .camera import CameraPose
from .file import FileHandler
from .log_handling import LOGGER
from .window import Window, WindowHandler


class App:
    def __init__(self, app_name: str = "JouleGL") -> None:
        self.name = app_name.lower().replace(" ", "-")
        FileHandler(data_path=os.getcwd()).read_statistics(app_name=self.name)
        self.window: Window = WindowHandler().create_window(self.name, title=app_name)
        self.window.set_callbacks(self.key_input, self.mouse_input)
        self.window.activate()
        LOGGER.info(
            f"OpenGL Version: {glGetIntegerv(GL_MAJOR_VERSION)}.{glGetIntegerv(GL_MINOR_VERSION)}"
        )

        self.fps: float = 120
        self.current_fps: float = 0
        self.frame_count: int = 0
        self.to_pause_time: float = 0
        self.last_frame_count: int = 0
        self.checked_frame_count: int = -1
        self.check_time: float = time.perf_counter()
        self.last_time: float = time.perf_counter()

        self.closed: bool = False

    def key_input(self, key, scancode, action, mods) -> bool:
        return False

    def mouse_input(self, button, action, mods) -> bool:
        pass

    def render(self) -> None:
        pass

    def frame(self) -> None:
        WindowHandler().update()
        clear_screen([1.0, 1.0, 1.0, 1.0])
        self.render()
        self.window.swap()

    def set_cam(
        self,
        base: np.ndarray = np.array([0.0, 0.0, 0.0]),
        offset_scale: float = 1.0,
        pose: CameraPose = CameraPose.LEFT,
    ) -> None:
        self.window.cam.update_base(base)
        self.window.cam.offset_scale = offset_scale
        self.window.cam.set_position(pose)

    def start(self) -> None:
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
            self.frame_count += 1

            if time.perf_counter() - self.check_time > 1.0:
                self.current_fps = float(
                    self.frame_count - self.checked_frame_count
                ) / (time.perf_counter() - self.check_time)
                self.checked_frame_count = self.frame_count
                self.check_time = time.perf_counter()

            current_time: float = time.perf_counter()
            elapsed_time: float = current_time - self.last_time
            if elapsed_time < 1.0 / self.fps:
                if elapsed_time > 0.001:
                    self.to_pause_time += (
                        float(self.frame_count - self.last_frame_count) / self.fps
                    ) - elapsed_time
                    self.last_frame_count = self.frame_count
                    self.last_time = current_time

                if self.to_pause_time > 0.005:
                    time.sleep(self.to_pause_time)
                    paused_for: float = time.perf_counter() - current_time
                    self.to_pause_time -= paused_for
                    self.last_time += paused_for
            else:
                self.last_frame_count = self.frame_count
                self.last_time = current_time
                self.to_pause_time = (
                    0
                    if self.to_pause_time < 0
                    else self.to_pause_time - (elapsed_time - 1.0 / self.fps)
                )
        self.cleanup()

    def cleanup(self) -> None:
        FileHandler(data_path=os.getcwd()).write_statistics(app_name=self.name)
        WindowHandler().destroy()
