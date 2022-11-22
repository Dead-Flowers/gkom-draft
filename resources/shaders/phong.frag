#version 330 core

in vec3 frag_position;
in vec3 frag_normal;

out vec4 frag_color;

vec3 light_position = vec3(4.0, 0.0, -5.0);
vec3 light_diffuse = vec3(1.0);
vec3 light_ambient = light_diffuse * 0.1;
vec3 light_specular = light_diffuse * 0.5;

vec3 obj_diffuse = vec3(0.0, 0.5, 0.5);
vec3 obj_specular = vec3(0.5);
float obj_shininess = 32.0;

uniform vec3 camera_position;

vec3 phong() {
    vec3 light_dir = normalize(light_position - frag_position);
    vec3 view_dir = normalize(camera_position - frag_position);
    vec3 reflect_dir = normalize(reflect(-light_dir, frag_normal));

	vec3 ambient = light_ambient * obj_diffuse;
    vec3 diffuse = max(dot(frag_normal, light_dir), 0.0) * light_diffuse * obj_diffuse;
    vec3 specular = pow(max(dot(view_dir, reflect_dir), 0.0), obj_shininess) * light_specular * obj_specular;

    return ambient + diffuse + specular;
}

void main() {
    frag_color = vec4(phong(), 1.0);
}