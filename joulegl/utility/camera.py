import math
from enum import IntFlag, auto
from math import asin, atan2, cos, degrees, radians, sin

import numpy as np


class CameraPose(IntFlag):
    FRONT = auto()
    BACK = auto()
    RIGHT = auto()
    LEFT = auto()
    UP = auto()
    DOWN = auto()


def get_cam_offset(pose: CameraPose) -> np.ndarray:
    x = 1.0 if pose & CameraPose.RIGHT else -1.0 if pose & CameraPose.LEFT else 0.0
    y = 1.0 if pose & CameraPose.UP else -1.0 if pose & CameraPose.DOWN else 0.0
    z = 1.0 if pose & CameraPose.BACK else -1.0 if pose & CameraPose.FRONT else 0.0
    cam_offset: np.ndarray = np.array([x, y, z], dtype=np.float32)
    return normalize(cam_offset)


def look_at(
    position: np.ndarray, target: np.ndarray, world_up: np.ndarray
) -> np.ndarray:
    z_axis: np.ndarray = normalize(position - target)
    x_axis = normalize(np.cross(normalize(world_up), z_axis))
    y_axis: np.ndarray = np.cross(z_axis, x_axis)

    translation: np.ndarray = np.identity(4, dtype=np.float32)
    translation[3][0] = -position[0]
    translation[3][1] = -position[1]
    translation[3][2] = -position[2]

    rotation: np.ndarray = np.identity(4, dtype=np.float32)
    rotation[0][0] = x_axis[0]
    rotation[1][0] = x_axis[1]
    rotation[2][0] = x_axis[2]
    rotation[0][1] = y_axis[0]
    rotation[1][1] = y_axis[1]
    rotation[2][1] = y_axis[2]
    rotation[0][2] = z_axis[0]
    rotation[1][2] = z_axis[1]
    rotation[2][2] = z_axis[2]

    return np.dot(translation, rotation)


def create_perspective_projection_matrix(fovy, aspect, near, far) -> np.ndarray:
    ymax = near * np.tan(fovy * np.pi / 360.0)
    xmax = ymax * aspect

    perspective_matrix = np.zeros((4, 4), dtype=np.float32)
    perspective_matrix[0, 0] = near / xmax
    perspective_matrix[1, 1] = near / ymax
    perspective_matrix[2, 2] = -(far + near) / (far - near)
    perspective_matrix[3, 2] = -2.0 * far * near / (far - near)
    perspective_matrix[2, 3] = -1.0
    return perspective_matrix


def normalize(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


class Camera:
    def __init__(
        self,
        width: float,
        height: float,
        base: np.ndarray,
        move_speed: float = 0.1,
        rotation: bool = False,
        rotation_speed: float = -0.25,
        offset_scale: float = 1.0,
    ) -> None:
        self.screen_width: float = width
        self.screen_height: float = height
        self.base: np.ndarray = base
        self.camera_pos: np.ndarray = self.base + np.array(
            [-3.0, 0.0, 0.0], dtype=np.float32
        )
        self.camera_front: np.ndarray = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.camera_up: np.ndarray = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.camera_right: np.ndarray = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        self.move_vector: np.ndarray = np.array([0, 0, 0], dtype=np.float32)
        self.move_speed: float = move_speed

        self.yaw: float = 0.0
        self.pitch: float = 0.0
        self.rotation_speed: float = rotation_speed
        self.offset_scale: float = offset_scale

        self.projection: np.ndarray = create_perspective_projection_matrix(
            45, width / height, 0.1, 1000
        )
        self.view: np.ndarray = self.generate_view_matrix()
        self.rotate_around_base: bool = rotation
        self.yaw_offset: float = 0.0
        self.zoom: float = 0.0
        self.update_camera_vectors()

    def update(self) -> None:
        self.update_camera_vectors()
        self.generate_view_matrix()

    def generate_view_matrix(self) -> np.ndarray:
        self.view = look_at(
            self.camera_pos, self.camera_pos + self.camera_front, self.camera_up
        )
        return self.view

    def process_mouse_movement(
        self, x_offset: float, y_offset: float, constrain_pitch: bool = True
    ) -> None:
        self.yaw -= x_offset * self.rotation_speed
        self.pitch += y_offset * self.rotation_speed

        if constrain_pitch:
            if self.pitch > 90.0:
                self.pitch = 90.0
            if self.pitch < -90.0:
                self.pitch = -90.0

    def calculate_direction(self) -> np.ndarray:
        front: np.ndarray = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        front[2] = cos(radians(self.yaw + self.yaw_offset)) * cos(radians(self.pitch))
        front[1] = -sin(radians(self.pitch))
        front[0] = sin(radians(self.yaw + self.yaw_offset)) * cos(radians(self.pitch))
        front = normalize(front)
        return -front

    def update_camera_vectors(self) -> None:
        if not self.rotate_around_base:
            # TODO: only update if pitch or yaw changed
            front: np.ndarray = self.calculate_direction()
        else:
            self.yaw_offset += self.rotation_speed
            front: np.ndarray = self.calculate_direction()
            front_offset = front - self.camera_front
            self.zoom -= self.move_vector[2] * 0.05
            self.camera_pos -= front_offset * np.linalg.norm(
                self.camera_pos - self.base
            )
            self.camera_pos = normalize(self.camera_pos - self.base)
            self.camera_pos = (
                self.camera_pos * self.offset_scale * (math.pow(1.5, self.zoom))
                + self.base
            )
            self.move_vector[0] = 0.0
            self.move_vector[1] = 0.0
            self.move_vector[2] = 0.0

        # TODO: only update if front changed
        self.camera_front = front
        self.camera_right = normalize(
            np.cross(self.camera_front, np.array([0.0, 1.0, 0.0], dtype=np.float32))
        )
        self.camera_up = normalize(np.cross(self.camera_right, self.camera_front))
        self.camera_pos = (
            self.camera_pos + self.camera_right * self.move_vector[0] * self.move_speed
        )
        self.camera_pos = (
            self.camera_pos + self.camera_up * self.move_vector[1] * self.move_speed
        )
        self.camera_pos = (
            self.camera_pos + self.camera_front * self.move_vector[2] * self.move_speed
        )

    def set_size(self, width: float, height: float) -> None:
        self.screen_width = width
        self.screen_height = height
        self.projection = create_perspective_projection_matrix(
            45, width / height, 0.1, 100
        )

    def move(self, direction: np.ndarray) -> None:
        self.move_vector[0] = (
            self.move_vector[0] if self.move_vector[0] != 0 else direction[0]
        )
        self.move_vector[1] = (
            self.move_vector[1] if self.move_vector[1] != 0 else direction[1]
        )
        self.move_vector[2] = (
            self.move_vector[2] if self.move_vector[2] != 0 else direction[2]
        )

    def stop(self, direction: np.ndarray) -> None:
        self.move_vector[0] = (
            0 if self.move_vector[0] == direction[0] else self.move_vector[0]
        )
        self.move_vector[1] = (
            0 if self.move_vector[1] == direction[1] else self.move_vector[1]
        )
        self.move_vector[2] = (
            0 if self.move_vector[2] == direction[2] else self.move_vector[2]
        )

    def set_position(self, camera_pose: CameraPose) -> None:
        self.move_vector = np.array([0, 0, 0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.camera_pos = self.base + get_cam_offset(camera_pose) * self.offset_scale
        self.camera_front = normalize(self.camera_pos - self.base)
        self.set_yaw_pitch_from_front()
        self.camera_right = normalize(np.cross(self.camera_up, self.camera_front))
        self.yaw_offset = 0.0
        self.zoom = 0.0

    def set_yaw_pitch_from_front(self) -> None:
        self.pitch = degrees(asin(-self.camera_front[1]))
        self.yaw = degrees(atan2(self.camera_front[0], self.camera_front[2]))

    def update_base(self, new_base: np.ndarray) -> None:
        self.camera_pos = self.camera_pos + (new_base - self.base)
        self.base = new_base
        self.update()

    def rotate(self) -> None:
        swap: bool = self.rotate_around_base
        self.rotate_around_base = True
        self.update()
        self.rotate_around_base = swap
