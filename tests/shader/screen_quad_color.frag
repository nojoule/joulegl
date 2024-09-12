#version 410

in vec4 vs_color;
out vec4 frag_color;

void main()
{
    frag_color = vec4(vs_color.xyz, 1.0);
}
