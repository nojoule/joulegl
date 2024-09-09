#version 440

layout(location = 0) in vec4 position;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * vec4(position.xyz, 1.0);
}
