#version 460 core

uniform vec3 Color;

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

out vec3 frag_position;
out vec3 frag_normal;
out vec3 object_color;
out vec4 shadow_coords[10];

uniform mat4 transform;

layout(std430, binding = 1) buffer shadow_buf {
    mat4 lights_shadow_bias[];
};

void main() {
    frag_position = in_position;
    frag_normal = normalize(in_normal);
    object_color = Color;
    gl_Position = transform * vec4(in_position, 1.0);
    for (int i = 0; i < lights_shadow_bias.length(); i++) {
        shadow_coords[i] = lights_shadow_bias[i] * vec4(in_position, 1.0);
    }
}