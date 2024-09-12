
#version 440

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;

out vec4 vs_color;

void main()
{
    vs_color = color;
    float offset = 1.0;
    if (color.r == 1.0) {
        offset = 0.0;
    }
    gl_Position = vec4(position.x * 0.5 - 0.5 + offset, position.y, position.z, 1.0);
}
