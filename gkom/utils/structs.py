from dataclasses import dataclass
from struct import Struct
from typing import BinaryIO, ClassVar


@dataclass
class Light:
    _struct: ClassVar[Struct] = Struct("3f4x3f4x3f4x3f4x")

    position: tuple[float, float, float]
    diffuse: tuple[float, float, float]
    specular: tuple[float, float, float]
    direction: tuple[float, float, float]

    def pack(self):
        return self._struct.pack(*self.position, *self.diffuse, *self.specular, *self.direction)

    @classmethod
    def unpack(cls, buffer: bytes):
        data = cls._struct.unpack(buffer)
        return cls(position=data[:3], diffuse=data[3:6], specular=data[6:9], direction=data[9:])
