#version 410

out vec4 frag_color;

uniform vec3 color = vec3(0.0, 0.0, 0.0);

void main()
{
    frag_color = vec4(color.xyz, 1.0);
}
