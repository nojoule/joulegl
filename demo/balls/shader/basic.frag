#version 440

in float depth;

out vec4 frag_color;

void main()
{
    float scaled_depth = (10.0 - depth) / 100.0;
    frag_color = vec4(0.0, 0.0, 0.0, scaled_depth);
}
