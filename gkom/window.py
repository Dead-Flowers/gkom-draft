from collections import defaultdict
from pathlib import Path
from typing import Any

import moderngl
import typed_settings as ts
from moderngl_window import WindowConfig
from moderngl_window.context.base import KeyModifiers
from pyrr import Matrix44

from gkom.camera import Camera
from gkom.config import Config, Object
from gkom.utils.shader import get_shaders
from gkom.utils.structs import Light


class Model:
    def __init__(self, obj: Object, model, prog):
        self.model = model
        self.vao = model.root_nodes[0].mesh.vao.instance(prog)
        self.position = obj.position
        self.rotation = obj.rotation
        self.scale = obj.scale
        self.color = obj.color


class GkomWindowConfig(WindowConfig):
    gl_version = (4, 6)
    title = "GKOM"

    resource_root_dir = (Path(__file__).parent.parent / "resources").resolve()
    resource_dir = resource_root_dir / "models"
    shader_dir = resource_root_dir / "shaders"
    config_path = resource_root_dir / "config.toml"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.config: Config = ts.load(Config, "gkom", [self.config_path])
        self.keys: dict[Any, bool] = defaultdict(lambda: False)

        shaders = get_shaders(self.shader_dir)
        self.program = shaders["phong"].create_program(self.ctx)

        self.camera = Camera(self.aspect_ratio)

        self.load_config()
        self.init_uniforms()

    def load_config(self):
        self.models = []
        for obj in self.config.object:
            self.models.append(
                Model(
                    obj,
                    self.load_scene(self.resource_dir / f"{obj.model}.obj"),
                    self.program,
                )
            )

        lights = bytearray()

        for light in self.config.light:
            lights += Light(light.position, light.diffuse, light.specular).pack()

        self.lights_buffer = self.ctx.buffer(lights)
        self.lights_buffer.bind_to_storage_buffer(0)

    def init_uniforms(self):
        self.transform = self.program["transform"]
        self.color = self.program["Color"]

    def render(self, time: float, frame_time: float):
        self.ctx.clear(1.0, 1.0, 1.0)         
        self.ctx.enable(moderngl.DEPTH_TEST | self.ctx.CULL_FACE)
        for model in self.models:
            translation = Matrix44.from_translation(model.position, dtype="f4")
            rotation = Matrix44.from_eulers(model.rotation, dtype="f4")
            model_matrix = translation * rotation

            self.camera.move(self.wnd.keys, self.keys, frame_time)

            self.color.value = model.color
            self.transform.write((self.camera.transform * model_matrix).astype("f4"))

            model.vao.render(moderngl.TRIANGLES)

    def key_event(self, key: Any, action: Any, modifiers: KeyModifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.keys[key] = False

    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        self.camera.look_around(dx, dy)
