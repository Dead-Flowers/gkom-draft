from collections import defaultdict
from pathlib import Path
from typing import Any

import moderngl
import typed_settings as ts
from moderngl_window import WindowConfig, geometry
from moderngl_window.context.base import KeyModifiers

from .config import Config
from .utils.shader import get_shaders


class GkomWindowConfig(WindowConfig):
    gl_version = (3, 3)
    title = "GKOM"
    resource_root_dir = (Path(__file__).parent.parent / "resources").resolve()
    resource_dir = resource_root_dir / "models"
    shader_dir = resource_root_dir / "shaders"
    config_path = resource_root_dir / "config.toml"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.config = ts.load(Config, "gkom", [self.config_path])
        self.keys: dict[Any, bool] = defaultdict(lambda: False)

        shaders = get_shaders(self.shader_dir)
        self.program = shaders["phong"].create_program(self.ctx)

        self.model_load()
        self.init_uniforms()

    def model_load(self):
        if self.argv.model_name:
            self.obj = self.load_scene(self.argv.model_name)
            self.vao = self.obj.root_nodes[0].mesh.vao.instance(self.program)
        else:
            self.vao = geometry.quad_2d((2, 2)).instance(self.program)

    def init_uniforms(self):
        self.transform = self.program["transform"]

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)

    def key_event(self, key: Any, action: Any, modifiers: KeyModifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.keys[key] = False

    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        ...
