from collections import defaultdict
from pathlib import Path
from typing import Any

import moderngl
import typed_settings as ts
from moderngl_window import WindowConfig, geometry
from moderngl_window.context.base import KeyModifiers
from pyrr import Matrix44

from gkom.camera import Camera
from gkom.config import Config, Object
from gkom.utils.shader import get_shaders


class Model:
    def __init__(self, obj: Object, model, prog):
        self.model = model
        self.vao = model.root_nodes[0].mesh.vao.instance(prog)
        self.position = obj.position
        self.rotation = obj.rotation
        self.scale = obj.scale
        self.color = obj.color


class GkomWindowConfig(WindowConfig):
    gl_version = (3, 3)
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

        self.model_load()
        self.init_uniforms()

    def model_load(self):
        self.models = []
        for obj in self.config.object:
            self.models.append(
                Model(
                    obj,
                    self.load_scene(self.resource_dir / f"{obj.model}.obj"),
                    self.program,
                )
            )

    def init_uniforms(self):
        self.transform = self.program["transform"]
        self.color = self.program["Color"]

    def render(self, time: float, frame_time: float):
        for model in self.models:
            translation = Matrix44.from_translation(model.position, dtype="f4")
            rotation = Matrix44.from_eulers(model.rotation, dtype="f4")
            model_matrix = translation * rotation

            self.camera.move(self.wnd.keys, self.keys, frame_time)

            self.color.value = model.color
            self.transform.write((self.camera.transform * model_matrix).astype("f4"))

            model.vao.render()

    def key_event(self, key: Any, action: Any, modifiers: KeyModifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.keys[key] = False

    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        self.camera.look_around(dx, dy)
