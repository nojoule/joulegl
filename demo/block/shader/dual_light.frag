#version 440

uniform float screen_width;
uniform float screen_height;

flat in vec3 gs_center_position;
in vec3 gs_frag_position;
flat in vec3 gs_color;

out vec4 frag_color;
layout (depth_greater) out float gl_FragDepth;

uniform mat4 projection;
uniform mat4 view;


const vec3 light_direction_cam_1 = normalize(vec3(1.0, 0.5, 0.75));
const vec3 light_direction_cam_2 = normalize(vec3(-1.0, 0.5, -0.75));
const vec3 atom_color_ambient  = vec3(0.2, 0.2, 0.2);
const vec3 atom_color_specular = vec3(0.1, 0.1, 0.1);

void main()
{
    vec3 normal = gs_frag_position - gs_center_position;
    float max_value = max(abs(normal.x), max(abs(normal.y), abs(normal.z)));

    bool x_near_max = max_value - abs(normal.x) < 0.03;
    bool y_near_max = max_value - abs(normal.y) < 0.03;
    bool z_near_max = max_value - abs(normal.z) < 0.03;

    if (int(x_near_max) + int(y_near_max) + int(z_near_max) > 1) {
        frag_color = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        if (abs(normal.x) == max_value) {
            normal = vec3(normal.x, 0.0, 0.0);
        } else {
            if (abs(normal.y) == max_value) {
                normal = vec3(0.0, normal.y, 0.0);
            } else {
                normal = vec3(0.0, 0.0, normal.z);
            }
        }
        normal = normalize(normal);
        frag_color = vec4(atom_color_ambient
        + (clamp(max(dot(normal, light_direction_cam_1), 0.0), 0.0, 1.0)
        + clamp(max(dot(normal, light_direction_cam_2), 0.0), 0.0, 1.0)) * gs_color
        , 1.0);
    }
}
