from typing import Literal

import typed_settings as ts


@ts.settings
class Object:
    model: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float]
    scale: tuple[float, float, float]
    color: tuple[float, float, float]
    shininess: float

@ts.settings
class Light:
    type: Literal["point"]
    position: tuple[float, float, float]
    diffuse: tuple[float, float, float]
    specular: tuple[float, float, float]


@ts.settings
class Config:
    object: list[Object]
    light: list[Light]
