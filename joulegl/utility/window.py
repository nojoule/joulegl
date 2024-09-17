from typing import Callable, Dict, Tuple

import glfw
import numpy as np
from OpenGL.GL import *

from .camera import Camera, CameraPose
from .window_config import WindowConfig


class BaseWindow:
    def __init__(self, config: WindowConfig) -> None:
        self.config: WindowConfig = config
        self.window_handle = glfw.create_window(
            config["width"], config["height"], config["title"], None, None
        )
        if not self.window_handle:
            raise Exception("glfw window can not be created!")

        self.active: bool = False

    def set_size(self, width: float, height: float) -> None:
        self.config["width"] = width
        self.config["height"] = height
        if self.active:
            glViewport(0, 0, width, height)

    def get_size(self) -> Tuple[float, float]:
        return self.config["width"], self.config["height"]

    def activate(self) -> None:
        if self.config["monitor_id"] is not None and 0 <= self.config[
            "monitor_id"
        ] < len(glfw.get_monitors()):
            glfw.set_window_pos(
                self.window_handle, self.config["screen_x"], self.config["screen_y"]
            )
        elif self.config["monitor_id"] is not None:
            self.config["screen_x"] = 0
            self.config["screen_y"] = 0
            glfw.set_window_pos(self.window_handle, 0, 0)

        glfw.get_current_context()
        glfw.make_context_current(self.window_handle)
        glfw.set_input_mode(self.window_handle, glfw.CURSOR, glfw.CURSOR_NORMAL)
        glViewport(0, 0, self.config["width"], self.config["height"])
        self.active = True

    def is_active(self) -> bool:
        return not glfw.window_should_close(self.window_handle)

    def swap(self) -> None:
        glfw.swap_buffers(self.window_handle)

    def poll(self) -> None:
        glfw.poll_events()

    def destroy(self) -> None:
        glfw.destroy_window(self.window_handle)


class Window(BaseWindow):
    def __init__(self, config: WindowConfig) -> None:
        super().__init__(config)
        self.cam: Camera = Camera(
            self.config["width"],
            self.config["height"],
            np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation=self.config["camera_rotation"],
            rotation_speed=self.config["camera_rotation_speed"],
        )

        self.last_mouse_pos: Tuple[int, int] = (
            int(self.config["width"] / 2),
            int(self.config["height"] / 2),
        )
        self.mouse_set: bool = False
        self.mouse_captured: bool = False
        self.focused: bool = True
        self.screenshot: bool = False
        self.record: bool = False
        self.frame_id: int = 0

        self.camera_movement_map: Dict[int, np.ndarray] = {
            glfw.KEY_W: np.array([0, 0, 1], dtype=np.float32),
            glfw.KEY_S: np.array([0, 0, -1], dtype=np.float32),
            glfw.KEY_A: np.array([-1, 0, 0], dtype=np.float32),
            glfw.KEY_D: np.array([1, 0, 0], dtype=np.float32),
        }

        self.camera_position_map: Dict[int, CameraPose] = {
            glfw.KEY_0: CameraPose.LEFT,
            glfw.KEY_1: CameraPose.FRONT,
            glfw.KEY_2: CameraPose.RIGHT,
            glfw.KEY_3: CameraPose(CameraPose.BACK | CameraPose.LEFT),
            glfw.KEY_4: CameraPose(CameraPose.FRONT | CameraPose.LEFT),
            glfw.KEY_5: CameraPose(CameraPose.UP | CameraPose.BACK | CameraPose.RIGHT),
            glfw.KEY_6: CameraPose(CameraPose.UP | CameraPose.BACK | CameraPose.LEFT),
            glfw.KEY_7: CameraPose(CameraPose.DOWN | CameraPose.BACK | CameraPose.LEFT),
            glfw.KEY_8: CameraPose.BACK,
            glfw.KEY_9: CameraPose.LEFT,
        }

    def set_size(self, width: float, height: float) -> None:
        super().set_size(width, height)
        self.cam.set_size(width, height)

    def set_callbacks(
        self,
        key_callback: Callable | None = None,
        mouse_callback: Callable | None = None,
    ) -> None:
        def resize_clb(glfw_window, width, height) -> None:
            self.config["screen_width"] = width
            self.config["screen_height"] = height
            self.config.store()

        def frame_resize_clb(glfw_window, width, height) -> None:
            self.set_size(width, height)

        def mouse_look_clb(glfw_window, x_pos, y_pos) -> None:
            if not self.focused or not self.mouse_captured:
                return

            if not self.mouse_set:
                self.last_mouse_pos = (x_pos, y_pos)
                self.mouse_set = True

            x_offset: float = x_pos - self.last_mouse_pos[0]
            y_offset: float = self.last_mouse_pos[1] - y_pos

            self.last_mouse_pos = (x_pos, y_pos)
            self.cam.process_mouse_movement(x_offset, y_offset)

        def mouse_button_clb(glfw_window, button: int, action: int, mods: int) -> None:
            if mouse_callback:
                if mouse_callback(button, action, mods):
                    return
            if not self.focused:
                return
            if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
                self.toggle_mouse_capture()

        def focus_clb(glfw_window, focused: int) -> None:
            if focused:
                self.focused = True
            else:
                self.focused = False

        def window_pos_clb(glfw_window, x_pos: int, y_pos: int) -> None:
            if len(glfw.get_monitors()) >= 1:
                for monitor_id, monitor in enumerate(glfw.get_monitors()):
                    m_x, m_y, width, height = glfw.get_monitor_workarea(monitor)
                    if m_x <= x_pos < m_x + width and m_y <= y_pos < m_y + height:
                        self.config["monitor_id"] = monitor_id
            self.config["screen_x"] = x_pos
            self.config["screen_y"] = y_pos
            self.config.store()

        def key_input_clb(glfw_window, key, scancode, action, mode) -> None:
            if not self.focused:
                return

            if key_callback:
                if key_callback(key, scancode, action, mode):
                    return

            if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
                glfw.set_window_should_close(glfw_window, True)

            if key in self.camera_movement_map:
                if action == glfw.PRESS:
                    self.cam.move(self.camera_movement_map[key])
                elif action == glfw.RELEASE:
                    self.cam.stop(self.camera_movement_map[key])

            if key == glfw.KEY_H and action == glfw.RELEASE:
                self.cam.rotate_around_base = not self.cam.rotate_around_base
                self.config["camera_rotation"] = self.cam.rotate_around_base
                self.config.store()

            if key == glfw.KEY_K and action == glfw.RELEASE:
                self.screenshot = True
            if key == glfw.KEY_R and action == glfw.RELEASE:
                self.record = not self.record

            if key in self.camera_position_map:
                if action == glfw.RELEASE:
                    self.cam.set_position(self.camera_position_map[key])

        glfw.set_window_size_callback(self.window_handle, resize_clb)
        glfw.set_framebuffer_size_callback(self.window_handle, frame_resize_clb)
        glfw.set_cursor_pos_callback(self.window_handle, mouse_look_clb)
        glfw.set_key_callback(self.window_handle, key_input_clb)
        glfw.set_mouse_button_callback(self.window_handle, mouse_button_clb)
        glfw.set_window_focus_callback(self.window_handle, focus_clb)
        glfw.set_window_pos_callback(self.window_handle, window_pos_clb)

    def update(self) -> None:
        self.cam.update()

    def toggle_mouse_capture(self) -> None:
        if self.mouse_captured:
            self.mouse_set = False
            glfw.set_input_mode(self.window_handle, glfw.CURSOR, glfw.CURSOR_NORMAL)
        else:
            self.mouse_set = False
            glfw.set_input_mode(self.window_handle, glfw.CURSOR, glfw.CURSOR_DISABLED)
        self.mouse_captured = not self.mouse_captured


class WindowHandler:
    def __init__(self) -> None:
        self.windows: Dict[str, Window] = dict()

        if not glfw.init():
            raise Exception("glfw can not be initialized!")

    def create_window(
        self,
        demo_name: str | None = None,
        hidden: bool = False,
        title: str = "JouleGL",
        transparent: bool = False,
        borderless: bool = False,
    ) -> Window:
        if hidden:
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        else:
            glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
        if transparent:
            glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        else:
            glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.FALSE)
        if borderless:
            glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        else:
            glfw.window_hint(glfw.DECORATED, glfw.TRUE)
        window_config: WindowConfig = WindowConfig(demo_name, title)
        window = Window(window_config)

        if self.windows.get(window_config["title"]):
            self.windows[window_config["title"]].destroy()

        self.windows[window_config["title"]] = window
        return window

    def get_window(self, title: str) -> None:
        window = self.windows[title]
        if not window:
            raise Exception("Requested window does not exist!")
        return window

    def destroy(self) -> None:
        for _, window in self.windows.items():
            if window.is_active():
                window.destroy()
        glfw.terminate()

    def update(self) -> None:
        glfw.poll_events()
        for _, window in self.windows.items():
            window.update()

    def close(self, window: Window) -> None:
        if window.is_active():
            window.destroy()
        self.windows.pop(window.config["title"])
