#version 460 core

layout(location=0) out vec4 out_color;
in vec2 uv;

uniform sampler2D texture0;

void main() {
    out_color = vec4(texture(texture0, uv).r);
}