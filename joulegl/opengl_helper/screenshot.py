import os
from datetime import datetime, timezone

import numpy as np
from OpenGL.GL import *
from PIL import Image

from ..utility.definitions import SCREENSHOT_PATH
from .frame_buffer import FrameBufferObject

screenshot_count: int = 0


def create_screenshot(
    width: int,
    height: int,
    network_name: str | None = None,
    frame_buffer: FrameBufferObject | None = None,
    frame_id: int | None = None,
) -> None:
    global screenshot_count
    screenshot_count += 1

    if frame_buffer is None:
        glReadBuffer(GL_FRONT)
    pixel_data = np.frombuffer(
        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        if frame_buffer is None
        else frame_buffer.read()
    )
    image: Image = Image.frombuffer("RGBA", (width, height), pixel_data)

    time_key: str = datetime.utcfromtimestamp(
        datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())
    ).strftime("%Y-%m-%d_%H_%M_%S_") + str(screenshot_count)

    os.makedirs(SCREENSHOT_PATH, exist_ok=True)
    if network_name is None:
        if frame_id is None:
            image.save(os.path.join(SCREENSHOT_PATH, "network_" + time_key + ".png"))
        else:
            image.save(
                os.path.join(SCREENSHOT_PATH, "network_" + str(frame_id) + ".png")
            )
    else:
        if frame_id is not None:
            image.save(
                os.path.join(
                    SCREENSHOT_PATH, network_name + "_" + str(frame_id) + ".png"
                )
            )
        else:
            image.save(
                os.path.join(SCREENSHOT_PATH, network_name + "_" + time_key + ".png")
            )
