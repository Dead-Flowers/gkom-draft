from dataclasses import dataclass
from struct import Struct
from typing import ClassVar

from moderngl import Program
from moderngl_window.scene import Scene
from pyrr import Matrix44, Vector3

from gkom.config import Light as ConfigLight
from gkom.config import Object


class Model:
    def __init__(
        self, obj: Object, model: Scene, light_prog: Program, shadow_prog: Program
    ):
        self.model = model
        self.light_vao = model.root_nodes[0].mesh.vao.instance(light_prog)
        self.shadow_vao = model.root_nodes[0].mesh.vao.instance(shadow_prog)
        self.position = obj.position
        self.rotation = obj.rotation
        self.scale = obj.scale
        self.color = obj.color
        self.shininess = obj.shininess

    @property
    def transform(self):
        translation = Matrix44.from_translation(self.position, dtype="f4")
        rotation = Matrix44.from_eulers(self.rotation, dtype="f4")
        scale = Matrix44.from_scale(self.scale, dtype="f4")
        return translation * rotation * scale


@dataclass
class Light:
    _struct: ClassVar[Struct] = Struct("3f4x3f4x3f4x3f4x")

    position: tuple[float, float, float]
    diffuse: tuple[float, float, float]
    specular: tuple[float, float, float]
    direction: tuple[float, float, float]

    @classmethod
    def from_config(cls, config_light: ConfigLight):
        return cls(
            position=config_light.position,
            diffuse=config_light.diffuse,
            specular=config_light.specular,
            direction=config_light.direction,
        )

    def pack(self):
        return self._struct.pack(
            *self.position, *self.diffuse, *self.specular, *self.direction
        )

    @classmethod
    def unpack(cls, buffer: bytes):
        data = cls._struct.unpack(buffer)
        return cls(
            position=data[:3], diffuse=data[3:6], specular=data[6:9], direction=data[9:]
        )

    def transform(self, object_position: Vector3):
        depth_projection = Matrix44.orthogonal_projection(
            -20, 20, -20, 20, -20, 40, dtype="f4"
        )
        depth_view = Matrix44.look_at(
            self.position, object_position, (0, 1, 0), dtype="f4"
        )
        return depth_projection * depth_view
