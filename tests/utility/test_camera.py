from math import isclose

import numpy as np
import pytest

from joulegl.utility.camera import Camera


def test_camera_basic() -> None:
    camera = Camera(800, 600, base=[0, 0, 0])
    assert camera.screen_width == 800
    assert camera.screen_height == 600
    assert camera.base == [0, 0, 0]
    assert camera.view.shape == (4, 4)
    assert camera.projection.shape == (4, 4)


@pytest.mark.parametrize("rotation_direction", ["-x", "+x", "-y", "+y", "--y", "++y"])
def test_camera_mouse_movement(rotation_direction: str) -> None:
    camera = Camera(800, 600, base=[0, 0, 0])
    x_offset = 0.1 if "x" in rotation_direction else 0.0
    y_offset = 0.1 if "y" in rotation_direction else 0.0
    if "-" in rotation_direction:
        x_offset *= -1
        y_offset *= -1
    if "--y" in rotation_direction or "++y" in rotation_direction:
        y_offset *= 4000
    previous_yaw = camera.yaw
    previous_pitch = camera.pitch
    constrain_pitch = "--y" in rotation_direction or "++y" in rotation_direction
    camera.process_mouse_movement(x_offset, y_offset, constrain_pitch=constrain_pitch)
    if "-x" in rotation_direction:
        assert camera.yaw < previous_yaw
    if "+x" in rotation_direction:
        assert camera.yaw > previous_yaw
    if "--y" in rotation_direction:
        assert camera.pitch == 90.0
    elif "-y" in rotation_direction:
        assert camera.pitch > previous_pitch
    if "++y" in rotation_direction:
        assert camera.pitch == -90.0
    elif "+y" in rotation_direction:
        assert camera.pitch < previous_pitch


@pytest.mark.parametrize("rotation_direction", ["x", "y", "yy", "xx"])
def test_camera_calculate_direction(rotation_direction: str) -> None:
    camera = Camera(800, 600, base=[0, 0, 0])
    assert camera.camera_front.shape == (3,)
    assert camera.camera_front[0] == 0.0
    assert camera.camera_front[1] == 0.0
    assert camera.camera_front[2] == -1.0

    direction = camera.calculate_direction()
    assert direction.shape == (3,)
    assert direction[0] == 0.0
    assert direction[1] == 0.0
    assert direction[2] == -1.0

    x_offset = 0.1 if "x" in rotation_direction else 0.0
    y_offset = 0.1 if "y" in rotation_direction else 0.0
    if "yy" in rotation_direction:
        y_offset *= 3600
    if "xx" in rotation_direction:
        x_offset *= 3600
    camera.process_mouse_movement(x_offset, y_offset)

    new_direction = camera.calculate_direction()
    assert direction.shape == (3,)
    if "xx" in rotation_direction or "yy" in rotation_direction:
        assert abs(np.dot(direction, new_direction)) < 0.01
    else:
        assert np.dot(direction, new_direction) > 0.99


def test_camera_set_size() -> None:
    camera = Camera(800, 600, base=[0, 0, 0])
    old_projection = camera.projection

    camera.set_size(400, 300)
    assert camera.screen_width == 400
    assert camera.screen_height == 300
    assert not np.array_equal(old_projection, camera.projection)


@pytest.mark.parametrize("x", [0.0, 0.1, -0.1])
@pytest.mark.parametrize("y", [0.0, 0.1, -0.1])
@pytest.mark.parametrize("z", [0.0, 0.1, -0.1])
def test_camera_movement(x: float, y: float, z: float) -> None:
    camera = Camera(800, 600, base=[0, 0, 0])
    camera.move(np.array([x, y, z]))
    original_pos = camera.camera_pos.copy()

    camera.update_camera_vectors()
    assert isclose(
        original_pos[0] + x * camera.move_speed, camera.camera_pos[0], abs_tol=0.0001
    )
    assert isclose(
        original_pos[1] + y * camera.move_speed, camera.camera_pos[1], abs_tol=0.0001
    )
    assert isclose(
        original_pos[2] + camera.camera_front[2] * z * camera.move_speed,
        camera.camera_pos[2],
        abs_tol=0.0001,
    )

    camera.update_camera_vectors()
    assert isclose(
        original_pos[0] + 2.0 * x * camera.move_speed,
        camera.camera_pos[0],
        abs_tol=0.0001,
    )
    assert isclose(
        original_pos[1] + 2.0 * y * camera.move_speed,
        camera.camera_pos[1],
        abs_tol=0.0001,
    )
    assert isclose(
        original_pos[2] + 2.0 * camera.camera_front[2] * z * camera.move_speed,
        camera.camera_pos[2],
        abs_tol=0.0001,
    )

    camera.stop(camera.move_vector)
    camera.update_camera_vectors()

    assert isclose(
        original_pos[0] + 2.0 * x * camera.move_speed,
        camera.camera_pos[0],
        abs_tol=0.0001,
    )
    assert isclose(
        original_pos[1] + 2.0 * y * camera.move_speed,
        camera.camera_pos[1],
        abs_tol=0.0001,
    )
    assert isclose(
        original_pos[2] + 2.0 * camera.camera_front[2] * z * camera.move_speed,
        camera.camera_pos[2],
        abs_tol=0.0001,
    )
