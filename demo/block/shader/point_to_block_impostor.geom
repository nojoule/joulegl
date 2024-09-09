#version 440

layout(points) in;
in float vs_discard[];
in vec3 vs_color[];

layout(triangle_strip, max_vertices = 36) out;

flat out vec3 gs_color;
flat out vec3 gs_center_position;
out vec3 gs_frag_position;

uniform mat4 projection;
uniform mat4 view;

void draw_vertex(vec3 position, vec3 offset)
{
    gl_Position = projection * view * vec4(position + 0.49999 * offset, 1.0);
    gs_frag_position = (vec4(position + 0.4 * offset, 1.0)).xyz;

    EmitVertex();
}

void main()
{
    vec3 position = gl_in[0].gl_Position.xyz;
    gs_center_position = position.xyz;
    gs_color = vs_color[0];

    if (vs_discard[0] == 0.0) {
        draw_vertex(position, vec3(-1.0, 1.0, -1.0));
        draw_vertex(position, vec3(1.0, 1.0, -1.0));
        draw_vertex(position, vec3(-1.0, -1.0, -1.0));
        draw_vertex(position, vec3(1.0, -1.0, -1.0));
        draw_vertex(position, vec3(1.0, -1.0, 1.0));
        draw_vertex(position, vec3(1.0, 1.0, -1.0));
        draw_vertex(position, vec3(1.0, 1.0, 1.0));
        draw_vertex(position, vec3(-1.0, 1.0, -1.0));
        draw_vertex(position, vec3(-1.0, 1.0, 1.0));
        draw_vertex(position, vec3(-1.0, -1.0, -1.0));
        draw_vertex(position, vec3(-1.0, -1.0, 1.0));
        draw_vertex(position, vec3(1.0, -1.0, 1.0));
        draw_vertex(position, vec3(-1.0, 1.0, 1.0));
        draw_vertex(position, vec3(1.0, 1.0, 1.0));
    }

    EndPrimitive();
}
