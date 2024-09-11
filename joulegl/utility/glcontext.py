import glfw

from joulegl.utility.window import BaseWindow
from joulegl.utility.window_config import WindowConfig


class GLContext:
    def __init__(self) -> None:
        pass

    def __enter__(self):
        glfw.init()
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        self.window = BaseWindow(WindowConfig())
        self.window.activate()

    def __exit__(self, *args):
        self.window.destroy()
        glfw.terminate()
