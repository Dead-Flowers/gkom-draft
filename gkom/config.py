from typing import Literal

import typed_settings as ts


@ts.settings
class Object:
    model: str
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    color: tuple[float, float, float] = (1.0, 1.0, 1.0)
    shininess: float = 32


@ts.settings
class Light:
    type: Literal["point"]
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    diffuse: tuple[float, float, float] = (1.0, 1.0, 1.0)
    specular: tuple[float, float, float] = (1.0, 1.0, 1.0)
    direction: tuple[float, float, float] = (0.0, 0.0, 0.0)


@ts.settings
class Config:
    object: list[Object]
    light: list[Light]
    shadow_map_resoultion: tuple[int, int]
