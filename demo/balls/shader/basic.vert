#version 440

layout(location = 0) in vec4 position;

uniform mat4 view;
uniform mat4 projection;
out float depth;

void main()
{
    depth = position.x;
    vec4 pos = view * vec4(position.xyz, 1.0);
    
    gl_Position = projection * pos;
}
