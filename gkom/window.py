from collections import defaultdict
from pathlib import Path
from typing import Any

import moderngl
import typed_settings as ts
from moderngl_window import WindowConfig
from moderngl_window.context.base import KeyModifiers
from pyrr import Matrix44, Vector3, matrix44, Vector4

from gkom.camera import Camera
from gkom.config import Config, Object
from gkom.utils.shader import get_shaders
from gkom.utils.structs import Light

BIAS_MATRIX = Matrix44(
    [[0.5, 0.0, 0.0, 0.0],
    [0.0, 0.5, 0.0, 0.0],
    [0.0, 0.0, 0.5, 0.0],
    [0.5, 0.5, 0.5, 1.0]],
    dtype='f4',
)

class Model:
    def __init__(self, obj: Object, model, light_prog, shodow_prog):
        self.model = model
        self.light_vao = model.root_nodes[0].mesh.vao.instance(light_prog)
        self.shadow_vao = model.root_nodes[0].mesh.vao.instance(shodow_prog)
        self.position = obj.position
        self.rotation = obj.rotation
        self.scale = obj.scale
        self.color = obj.color
        self.shininess = obj.shininess


class GkomWindowConfig(WindowConfig):
    gl_version = (4, 6)
    title = "GKOM"
    cursor = False

    resource_root_dir = (Path(__file__).parent.parent / "resources").resolve()
    resource_dir = resource_root_dir / "models"
    shader_dir = resource_root_dir / "shaders"
    config_path = resource_root_dir / "config.toml"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.config: Config = ts.load(Config, "gkom", [self.config_path])
        self.keys: dict[Any, bool] = defaultdict(lambda: False)

        shaders = get_shaders(self.shader_dir)
        self.light_prog = shaders["phong"].create_program(self.ctx)
        self.shadow_prog = shaders["shadow_map"].create_program(self.ctx)
        self.raw_depth_prog = shaders["raw_deph"].create_program(self.ctx)

        self.camera = Camera(self.aspect_ratio, position=Vector3((0.0, 5.0, 5.0)))
        self.wnd.mouse_exclusivity = True

        self.load_config()
        self.init_uniforms()
        self.init_shoadow_map()

    def load_config(self):
        self.models: list[Model] = []
        for obj in self.config.object:
            self.models.append(
                Model(
                    obj,
                    self.load_scene(self.resource_dir / f"{obj.model}.obj"),
                    self.light_prog,
                    self.shadow_prog
                )
            )

        lights = bytearray()

        for light in self.config.light:
            lights += Light(light.position, light.diffuse, light.specular, light.direction).pack()

        self.lights_buffer = self.ctx.buffer(lights)
        self.lights_buffer.bind_to_storage_buffer(0)
        
        self.lights_shadow = self.ctx.buffer(bytearray([0]*192))
        self.lights_shadow.bind_to_storage_buffer(1)

        self.shadow_cord_buf = self.ctx.buffer(bytearray(Vector4().tobytes()*len(self.config.light)))
        self.shadow_cord_buf.bind_to_storage_buffer(2)

    def init_shoadow_map(self):
        offscreen_size = self.config.shadow_map_resoultion
        self.offscreen_depth = self.ctx.depth_texture(offscreen_size)
        self.offscreen_depth.compare_func = ''
        self.offscreen_depth.repeat_x = False
        self.offscreen_depth.repeat_y = False
        self.offscreen_color = self.ctx.texture(offscreen_size, 4)

        self.offscreen = self.ctx.framebuffer(
            color_attachments=[self.offscreen_color],
            depth_attachment=self.offscreen_depth,
        )

    def init_uniforms(self):
        self.transform = self.light_prog["transform"]
        self.color = self.light_prog["Color"]
        self.camera_position = self.light_prog["camera_position"]
        self.shininess = self.light_prog["shininess"]
        self.shadow_mvp = self.shadow_prog["mvp"]

        self.light_prog["shadowMap"].value = 0

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.4, 0.4, 0.4)
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        
        # Pass 1
        self.offscreen.clear()
        self.offscreen.use()
        
        light_shadow = bytearray()

        for light in self.config.light:
            depth_projection = Matrix44.orthogonal_projection(-20, 20, -20, 20, -20, 40, dtype='f4')
            depth_view = Matrix44.look_at(light.position, (0, 0, 0), (0, 1, 0), dtype='f4')
            depth_mvp = depth_projection * depth_view
            self.shadow_mvp.write(depth_mvp.astype('f4'))

            light_shadow += matrix44.multiply(BIAS_MATRIX, depth_mvp).astype('f4').tobytes()

            for model  in self.models:
                model.shadow_vao.render()

        self.lights_shadow = self.ctx.buffer(light_shadow)
        self.lights_shadow.bind_to_storage_buffer(1)

        shadows_cords = self.shadow_cord_buf.read()

        # Pass 2 render scene
        self.wnd.use()
        for model in self.models:
            translation = Matrix44.from_translation(model.position, dtype="f4")
            rotation = Matrix44.from_eulers(model.rotation, dtype="f4")
            scale = Matrix44.from_scale(model.scale, dtype="f4")
            model_matrix = translation * rotation * scale

            self.camera.move(self.wnd.keys, self.keys, frame_time)

            self.camera_position.write(self.camera.position.astype("f4"))
            self.color.value = model.color
            self.transform.write((self.camera.transform * model_matrix).astype("f4"))
            self.shininess.value = model.shininess

            self.offscreen_depth.use(location=0)

            model.light_vao.render(moderngl.TRIANGLES)
    

        # Pass3 render shoadws 
        


    def key_event(self, key: Any, action: Any, modifiers: KeyModifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            self.keys[key] = True
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.keys[key] = False

    def mouse_position_event(self, x: int, y: int, dx: int, dy: int):
        self.camera.look_around(dx, dy)
