import os
from datetime import datetime, timezone

import numpy as np
from OpenGL.GL import *
from PIL import Image

from joulegl.utility.log_handling import LOGGER

from ..utility.definitions import SCREENSHOT_PATH
from .frame_buffer import FrameBufferObject

screenshot_count: int = 0


def create_screenshot(
    width: int,
    height: int,
    name: str | None = None,
    frame_buffer: FrameBufferObject | None = None,
    frame_id: int | None = None,
    path: str = SCREENSHOT_PATH,
) -> None:
    global screenshot_count
    screenshot_count += 1

    if frame_buffer is None:
        glReadBuffer(GL_FRONT)
    try:
        pixel_data = np.frombuffer(
            (
                glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
                if frame_buffer is None
                else frame_buffer.read()
            ),
            dtype=np.uint8,
        )
    except Exception as e:
        LOGGER.error(f"Screenshot failed: {e}")
        return

    # flip the image vertically
    pixel_data = np.flipud(pixel_data.reshape(height, width, 4))

    image: Image = Image.frombuffer("RGBA", (width, height), pixel_data.flatten())

    time_key: str = datetime.utcfromtimestamp(
        datetime.timestamp(datetime.now().replace(tzinfo=timezone.utc).astimezone())
    ).strftime("%Y-%m-%d_%H_%M_%S_") + str(screenshot_count)

    os.makedirs(path, exist_ok=True)
    if name is None:
        if frame_id is None:
            image.save(os.path.join(path, f"screenshot_{time_key}.png"))
        else:
            image.save(os.path.join(path, f"screenshot_{frame_id}.png"))
    else:
        if frame_id is None:
            image.save(os.path.join(path, f"{name}_{time_key}.png"))
        else:
            image.save(os.path.join(path, f"{name}_{frame_id}.png"))
