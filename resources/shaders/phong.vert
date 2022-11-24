#version 460 core

uniform vec3 Color;

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

out vec3 frag_position;
out vec3 frag_normal;
out vec3 object_color;

uniform mat4 transform;
uniform mat4 scale;

void main() {
    frag_position = in_position;
    frag_normal = normalize(in_normal);
    object_color = Color;
    gl_Position = transform * scale * vec4(in_position, 1.0);
}