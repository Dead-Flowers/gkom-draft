#version 460 core

struct Light {
    vec3 position;
    // float padding
    vec3 diffuse;
    // float padding
    vec3 specular;
    // float padding
};

in vec3 frag_position;
in vec3 frag_normal;
in vec3 object_color;

out vec4 color;

uniform float shininess;
uniform vec3 camera_position;

const vec3 light_ambient = vec3(0.1);

layout(std430, binding = 0) buffer light_buf {
    Light lights[];
};

vec3 pointLight(Light light, vec3 camera_position, vec3 object_color, float shininess) {
    vec3 light_dir = normalize(light.position - frag_position);
    vec3 view_dir = normalize(camera_position - frag_position);
    vec3 reflect_dir = normalize(reflect(-light_dir, frag_normal));

	vec3 ambient = light_ambient * object_color;
    vec3 diffuse = max(dot(frag_normal, light_dir), 0.0) * light.diffuse * object_color;
    vec3 specular = pow(max(dot(view_dir, reflect_dir), 0.0), shininess) * light.specular * object_color;

    return ambient + diffuse + specular;
}

void main() {
    for (int i = 0; i < lights.length(); i++) {
        color = vec4(pointLight(lights[i], camera_position, object_color, shininess), 1.0);
    }
}