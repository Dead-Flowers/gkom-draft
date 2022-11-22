import math
from typing import Any

from moderngl_window.context.base import BaseKeys
from pyrr import Matrix44, Vector3

SPEED = 0.1
MOUSE_SENSITIVITY = 0.015


def clamp(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value


class Camera:
    def __init__(
        self,
        aspect_ratio: float,
        position: Vector3 | None = None,
        yaw: float = -90.0,
        pitch: float = 0.0,
        up: Vector3 = Vector3((0.0, 1.0, 0.0)),
        fov: float = 60.0,
        near: float = 0.1,
        far: float = 1000.0,
    ) -> None:
        self.position = position or Vector3()
        self.yaw = math.radians(yaw)
        self.pitch = math.radians(pitch)
        self.up = self.world_up = up.normalized

        self.front = Vector3()
        self.right = Vector3()
        self.projection_matrix = Matrix44.perspective_projection(
            fov, aspect_ratio, near, far
        )

        self._recalculate_vectors()

    @property
    def transform(self):
        return self.projection_matrix * Matrix44.look_at(
            self.position, self.position + self.front, self.up
        )

    def move(self, keys: type[BaseKeys], key_state: dict[Any, bool], frame_time: float):
        if key_state[keys.W]:
            self.position += self.front * SPEED
        if key_state[keys.S]:
            self.position -= self.front * SPEED
        if key_state[keys.D]:
            self.position += self.right * SPEED
        if key_state[keys.A]:
            self.position -= self.right * SPEED

    def look_around(self, dx: int, dy: int):
        self.yaw += dx * MOUSE_SENSITIVITY
        self.pitch = clamp(
            self.pitch - dy * MOUSE_SENSITIVITY, -math.pi / 2.01, math.pi / 2.01
        )

        self._recalculate_vectors()

    def _recalculate_vectors(self):
        self.front = Vector3(
            (
                math.cos(self.yaw) * math.cos(self.pitch),
                math.sin(self.pitch),
                math.sin(self.yaw) * math.cos(self.pitch),
            )
        ).normalized
        self.right = self.front.cross(self.world_up).normalized
        self.up = self.right.cross(self.front).normalized
