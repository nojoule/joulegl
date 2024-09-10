import os
import threading
import time

import numpy as np

from joulegl.utility.app import App
from joulegl.utility.camera import CameraPose
from joulegl.utility.definitions import SCREENSHOT_PATH
from tests.conftest import delete_all_files_in_folder


class AppStatus:
    STARTED = 1
    CLOSED = 2


class WrappedApp:
    def __init__(self, name: str = "Test") -> None:
        self.name = name
        self.app: App | None = None
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

        # TODO: find a better way to wait for the app to start
        for _ in range(100):
            if self.app is not None:
                break
            time.sleep(0.01)

    def run(self):
        self.app = App(self.name)
        self.app.run()

    def close(self):
        self.app.close()
        self.thread.join()


def test_initialize_app() -> None:
    app = App("Test Test 1")
    assert app is not None
    assert app.title == "Test Test 1"
    assert app.name == "test-test-1"
    assert not app.closed
    assert app.window is not None

    app.close()


def test_app_close() -> None:
    wrapped_app = WrappedApp("Test Test 2")
    app = wrapped_app.app

    assert app is not None
    assert app.title == "Test Test 2"
    assert app.name == "test-test-2"
    assert not app.closed
    assert app.window is not None

    wrapped_app.close()
    assert app.closed


def test_app_cam_changes():
    wrapped_app = WrappedApp("Test")
    app = wrapped_app.app

    camera_position_before = app.window.cam.camera_pos
    app.set_cam([1.0, 2.0, 3.0], 4.0, CameraPose.RIGHT)
    assert app.window.cam.base == [1.0, 2.0, 3.0]
    assert app.window.cam.offset_scale == 4.0
    assert not np.array_equal(camera_position_before, app.window.cam.camera_pos)

    wrapped_app.close()


def test_app_screenshot():
    wrapped_app = WrappedApp("Test")
    app = wrapped_app.app

    delete_all_files_in_folder(SCREENSHOT_PATH)

    app.window.screenshot = True
    # TODO: find a better way to wait for the app to start
    for _ in range(100):
        if not app.window.screenshot:
            break
        time.sleep(0.01)
    assert app.window.screenshot is False

    found_screenshot = False
    for filename in os.listdir(SCREENSHOT_PATH):
        if filename.startswith("screenshot_"):
            found_screenshot = True
            break

    assert found_screenshot

    wrapped_app.close()


def test_app_record():
    wrapped_app = WrappedApp("Test")
    app = wrapped_app.app
    app.fps = 5

    delete_all_files_in_folder(SCREENSHOT_PATH)

    app.window.record = True
    maximum_wait_count = 100
    while app.window.frame_id < 3 or maximum_wait_count < 0:
        time.sleep(0.01)
        maximum_wait_count -= 1
    app.window.record = False

    found_screenshots = 0
    for filename in os.listdir(SCREENSHOT_PATH):
        if filename.startswith("screenshot_"):
            found_screenshots += 1

    assert found_screenshots > 1

    wrapped_app.close()


# TODO test def key_input mouse_input render
