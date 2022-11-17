from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from moderngl import Context

VERTEX_SHADER_EXTENSION = "vert"
FRAGMENT_SHADER_EXTENSION = "frag"


@dataclass
class ShaderCollection:
    vertex_shader: str | None = None
    fragment_shader: str | None = None

    def assign_shader(self, extension: str, shader_text: str):
        if extension == VERTEX_SHADER_EXTENSION:
            self.vertex_shader = shader_text
        elif extension == FRAGMENT_SHADER_EXTENSION:
            self.fragment_shader = shader_text

    def is_complete(self):
        return self.vertex_shader and self.fragment_shader

    def create_program(self, context: Context):
        return context.program(
            vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader
        )


def get_shaders(path: Path):
    shaders: dict[str, ShaderCollection] = defaultdict(ShaderCollection)

    for file in path.iterdir():
        if file.is_file():
            shaders[file.stem].assign_shader(file.suffix[1:], file.read_text())

    if not all(collection.is_complete() for collection in shaders.values()):
        raise RuntimeError("Some shaders are missing")

    return shaders
