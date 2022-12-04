#version 460 core

struct Light {
    vec3 position;
    // float padding
    vec3 diffuse;
    // float padding
    vec3 specular;
    // float padding
    vec3 direction;
};

in vec3 frag_position;
in vec3 frag_normal;
in vec3 object_color;

out vec4 color;

uniform float shininess;
uniform vec3 camera_position;
uniform sampler2D shadowMap;

const vec3 light_ambient = vec3(0.1);
const float att_constant = 0.1;
const float att_linear = 0.05;
const float att_quadratic = 0.01;
float bias = 0.005;

layout(std430, binding = 0) buffer light_buf {
    Light lights[];
};

layout(std430, binding = 2) buffer shadow_cord_buf {
    vec4 shadow_cord[];
};

vec3 pointLight(Light light, vec3 camera_position, vec3 object_color, float shininess) {
    vec3 light_dir = normalize(-light.direction);
    // vec3 light_dir = normalize(light.position - frag_position);
    vec3 view_dir = normalize(camera_position - frag_position);
    vec3 reflect_dir = normalize(reflect(-light_dir, frag_normal));

    float distance = length(light.position - frag_position);
    // float attenuation = 1.0 / (att_constant + att_linear * distance + att_quadratic * distance * distance);
    float attenuation = 1.0;
	vec3 ambient = light_ambient * object_color * attenuation;
    vec3 diffuse = max(dot(frag_normal, light_dir), 0.0) * light.diffuse * object_color * attenuation;
    vec3 specular = pow(max(dot(view_dir, reflect_dir), 0.0), shininess) * light.specular * object_color * attenuation;

    return ambient + diffuse + specular;
}

void main() {
    vec3 temp = vec3(0.0);
    for (int i = 0; i < lights.length(); i++) {
        float visibility = 1.0;
        if (texture(shadowMap, shadow_cord[i].xy ).r <  shadow_cord[i].z - bias){
            visibility = 0.1;
        }
        temp += visibility * pointLight(lights[i], camera_position, object_color, shininess);
    }
    color = vec4(temp, 1.0);
}