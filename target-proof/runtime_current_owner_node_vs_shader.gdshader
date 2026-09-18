shader_type spatial;

uniform float driver_deg = 0.0;
uniform vec3 driver_axis = vec3(0.0, 1.0, 0.0);
uniform vec4 albedo_color : source_color = vec4(1.0);
uniform float metallic_value = 0.0;
uniform float roughness_value = 1.0;
uniform float specular_value = 0.5;

vec3 rotate_axis(vec3 v, vec3 axis, float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return v * c + cross(axis, v) * s + axis * dot(axis, v) * (1.0 - c);
}

void vertex() {
    vec3 axis = normalize(driver_axis);
    float angle = driver_deg * PI / 180.0;
    VERTEX = rotate_axis(VERTEX, axis, angle);
    NORMAL = normalize(rotate_axis(NORMAL, axis, angle));
}

void fragment() {
    ALBEDO = albedo_color.rgb;
    METALLIC = metallic_value;
    ROUGHNESS = roughness_value;
    SPECULAR = specular_value;
}
