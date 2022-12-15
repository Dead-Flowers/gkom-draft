#version 460 core

struct Light {
    vec3 position;
    // float padding
    vec3 diffuse;
    // float padding
    vec3 specular;
    // float padding
    vec3 direction;
    // float padding
};

in vec3 frag_position;
in vec3 frag_normal;
in vec3 object_color;
in vec4 shadow_coords[10];

out vec4 color;

uniform float shininess;
uniform vec3 camera_position;
uniform sampler2D shadowMaps[10];

const vec3 light_ambient = vec3(0.1);
const float att_constant = 0.1;
const float att_linear = 0.05;
const float att_quadratic = 0.01;
float bias = 0.006;

vec2 poissonDisk[4] = vec2[](
  vec2( -0.94201624, -0.39906216 ),
  vec2( 0.94558609, -0.76890725 ),
  vec2( -0.094184101, -0.92938870 ),
  vec2( 0.34495938, 0.29387760 )
);


layout(std430, binding = 0) buffer light_buf {
    Light lights[];
};

float shadow(sampler2D shadow_map, vec4 shadow_coords) {
    float visibility = 1.0;
    vec3 proj_coords = shadow_coords.xyz;
    float current_depth = proj_coords.z - 0.005;
    for (int i=0; i<4; i++) {
        float closest_depth = texture(shadow_map, proj_coords.xy + poissonDisk[i]/800.0).r;
        if (current_depth > closest_depth) {
            visibility -= 0.23;
        }
    }
    return visibility;
    // return current_depth > closest_depth ? 0.38 : 1.0;
}

vec3 pointLight(Light light, sampler2D shadow_map, vec4 shadow_coords, vec3 camera_position, vec3 object_color, float shininess) {
    vec3 light_dir = normalize(-light.direction);
    // vec3 light_dir = normalize(light.position - frag_position);
    vec3 view_dir = normalize(camera_position - frag_position);
    vec3 reflect_dir = normalize(reflect(-light_dir, frag_normal));

    float distance = length(light.position - frag_position);
    // float attenuation = 1.0 / (att_constant + att_linear * distance + att_quadratic * distance * distance);
    float attenuation = 1.0;
    float shadow = shadow(shadow_map, shadow_coords);
	vec3 ambient = light_ambient * object_color * attenuation;
    vec3 diffuse = max(dot(frag_normal, light_dir), 0.0) * light.diffuse * object_color * attenuation;
    vec3 specular = pow(max(dot(view_dir, reflect_dir), 0.0), shininess) * light.specular * object_color * attenuation;
    return shadow * (ambient + diffuse + specular);
}

void main() {
    vec3 temp = vec3(0.0);
    for (int i = 0; i < lights.length(); i++) {
        temp += pointLight(lights[i], shadowMaps[i], shadow_coords[i], camera_position, object_color, shininess);
    }
    color = vec4(temp, 1.0);
}