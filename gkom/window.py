import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import moderngl
import numpy as np
import typed_settings as ts
from moderngl import Framebuffer, Texture
from moderngl_window import WindowConfig
from moderngl_window.context.base import KeyModifiers
from PIL import Image
from pyrr import Matrix44, Vector3

from gkom.camera import Camera
from gkom.config import Config
from gkom.utils import Light, Model
from gkom.utils.shader import get_shaders

BIAS_MATRIX = Matrix44(
    [
        [0.5, 0.0, 0.0, 0.0],
        [0.0, 0.5, 0.0, 0.0],
        [0.0, 0.0, 0.5, 0.0],
        [0.5, 0.5, 0.5, 1.0],
    ],
    dtype="f4",
)


class GkomWindowConfig(WindowConfig):
    gl_version = (4, 6)
    title = "GKOM"
    cursor = False

    resource_root_dir = (Path(__file__).parent.parent / "resources").resolve()
    resource_dir = resource_root_dir / "models"
    shader_dir = resource_root_dir / "shaders"
    config_path = resource_root_dir / "config.toml"
    shadow_map_dir = (Path(__file__).parent.parent / "shadow-maps").resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.config: Config = ts.load(Config, "gkom", [self.config_path])
        self.keys: dict[Any, bool] = defaultdict(lambda: False)
        self.models: list[Model] = []
        self.lights: list[Light] = []
        self.captured_shadow_maps = False

        shaders = get_shaders(self.shader_dir)
        self.light_prog = shaders["phong"].create_program(self.ctx)
        self.shadow_prog = shaders["shadow_map"].create_program(self.ctx)
        self.raw_depth_prog = shaders["raw_deph"].create_program(self.ctx)

        self.camera = Camera(self.aspect_ratio, position=Vector3((0.0, 5.0, 5.0)))
        self.wnd.mouse_exclusivity = True

        self.load_config()
        self.init_uniforms()
        self.init_shadow_map()

    def load_config(self):
        for obj in self.config.object:
            self.models.append(
                Model(
                    obj,
                    self.load_scene(str(self.resource_dir / f"{obj.model}.obj")),
                    self.light_prog,
                    self.shadow_prog,
                )
            )

        lights_data = bytearray()

        for config_light in self.config.light:
            light = Light(
                config_light.position,
                config_light.diffuse,
                config_light.specular,
                config_light.direction,
            )
            self.lights.append(light)
            lights_data += light.pack()

        self.lights_buffer = self.ctx.buffer(lights_data)
        self.lights_buffer.bind_to_storage_buffer(0)

        self.lights_shadow = self.ctx.buffer(
            Matrix44().astype("f4").tobytes() * len(self.config.light)
        )
        self.lights_shadow.bind_to_storage_buffer(1)

    def init_shadow_map(self):
        self.depth_textures: list[Texture] = []
        self.fbos: list[Framebuffer] = []
        shadow_resolution = self.config.shadow_map_resoultion

        for _ in range(len(self.config.light)):
            depth_tex = self.ctx.depth_texture(shadow_resolution, alignment=4)
            depth_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            depth_tex.repeat_x = True
            depth_tex.repeat_y = True

            self.depth_textures.append(depth_tex)
            self.fbos.append(
                self.ctx.framebuffer(
                    depth_attachment=depth_tex,
                )
            )

    def init_uniforms(self):
        self.transform = self.light_prog["transform"]
        self.color = self.light_prog["Color"]
        self.camera_position = self.light_prog["camera_position"]
        self.shininess = self.light_prog["shininess"]
        self.shadow_mvp = self.shadow_prog["mvp"]

        self.light_prog["shadowMaps"].value = [(i,) for i in range(10)]

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.4, 0.4, 0.4)
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        model_shadow_mvps: dict[int, bytearray] = defaultdict(bytearray)

        # Pass 1
        for light, fbo in zip(self.lights, self.fbos):
            fbo.use()
            fbo.clear()

            for i, model in enumerate(self.models):
                shadow_mvp = light.transform(Vector3(light.direction)) * model.transform
                self.shadow_mvp.write(shadow_mvp.astype("f4"))

                model_shadow_mvps[i] += (
                    (BIAS_MATRIX * shadow_mvp).astype("f4").tobytes()
                )

                model.shadow_vao.render(moderngl.TRIANGLES)

        # Pass 2 render scene
        self.wnd.use()

        for i, model in enumerate(self.models):
            self.camera.move(self.wnd.keys, self.keys, frame_time)

            self.camera_position.write(self.camera.position.astype("f4"))
            self.color.value = model.color
            self.transform.write((self.camera.transform * model.transform).astype("f4"))
            self.shininess.value = model.shininess
            self.lights_shadow.write(model_shadow_mvps[i])

            for i, tex in enumerate(self.depth_textures):
                tex.use(location=i)

            model.light_vao.render(moderngl.TRIANGLES)

        if not self.captured_shadow_maps:
            self.captured_shadow_maps = True
            self.shadow_map_dir.mkdir(parents=True, exist_ok=True)
            for i, tex in enumerate(self.depth_textures):
                temp_v = (np.frombuffer(tex.read(), dtype="f4") * 255).astype(np.uint8)

                Image.frombytes("L", tex.size, temp_v).save(
                    self.shadow_map_dir / f"{i}.png"
                )

    def key_event(self, key: Any, action: Any, modifiers: KeyModifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.keys[key] = False

    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        self.camera.look_around(dx, dy)
