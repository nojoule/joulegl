#version 440

layout(location = 0) in vec4 position;

out vec3  vs_normal;
out float vs_discard;
out float vs_size;
out vec4 vs_color;

uniform mat4 view;

void main()
{
    gl_Position = view * vec4(position.xyz, 1.0);
    vec4 new_normal = view * vec4((position.xyz + vec3(0.0, 1.0, 0.0)), 1.0);
    vs_normal = normalize(vec3(new_normal.xyz - gl_Position.xyz));
    vs_size = position.w;
    vs_color = vec4(0.0, 0.0, 0.0, 1.0);
}
