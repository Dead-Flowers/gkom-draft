import math
from typing import Any

from moderngl_window.context.base import BaseKeys
from pyrr import Matrix44, Vector3

SPEED = 5
MOUSE_SENSITIVITY = 0.15


class Camera:
    def __init__(
        self,
        position: Vector3 | None = None,
        yaw: float = -90.0,
        pitch: float = 0.0,
        up: Vector3 = Vector3((0.0, 1.0, 0.0)),
    ) -> None:
        self.position = position or Vector3()
        self.yaw = math.radians(yaw)
        self.pitch = math.radians(pitch)
        self.up = self.world_up = up.normalized
        self.front = Vector3()
        self.right = Vector3()

        self._recalculate_vectors()

    def look_at_matrix(self):
        return Matrix44.look_at(self.position, self.position + self.front, self.up)

    def move(self, keys: BaseKeys, key_state: dict[Any, bool], frame_time: float):
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
        self.pitch += dy * MOUSE_SENSITIVITY

        if self.pitch > 89.999:
            self.pitch = 89.999
        elif self.pitch < -89.999:
            self.pitch = -89.999

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
