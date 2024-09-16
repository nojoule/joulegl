#version 410

layout(points) in;

layout(triangle_strip, max_vertices = 4) out;


void draw_vertex(vec3 position, vec3 offset)
{
    gl_Position = vec4(position + offset, 1.0);
    EmitVertex();
}

void main()
{
    vec3 position = gl_in[0].gl_Position.xyz;

    draw_vertex(position, vec3(0.0, 2.0, 0.0));
    draw_vertex(position, vec3(2.0, 2.0, 0.0));
    draw_vertex(position, vec3(0.0, 0.0, 0.0));
    draw_vertex(position, vec3(2.0, 0.0, 0.0));

    EndPrimitive();
}
