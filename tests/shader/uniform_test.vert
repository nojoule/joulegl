
#version 440

layout(location = 0) in vec4 position;

uniform float test_float = 1.0;
uniform vec3 test_vec3 = vec3(0.0, 0.0, 0.0);
uniform int test_int = 1;
uniform ivec3 test_ivec3 = ivec3(1, 1, 1);
uniform mat4 test_mat4 = mat4(1.0);

void main()
{

    gl_Position = vec4(position.xyz, test_mat4[0].x + test_float + test_vec3.x + float(test_int) + float(test_ivec3.x));
}
