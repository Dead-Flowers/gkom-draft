#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

out vec3 frag_position;
out vec3 frag_normal;

uniform mat4 transform;

void main() {
    frag_position = in_position;
    frag_normal = normalize(in_normal);
    gl_Position = transform * vec4(in_position, 1.0);
}