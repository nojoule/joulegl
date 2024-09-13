#version 440

layout (location=0) in vec4 position;

out float vs_density;
out float vs_discard;
out vec3 vs_color;

//$$const vec3 $$block_type_name$$ = vec3($$block_type2_name$$, $$block_type_g$$, $$block_type_b$$);

void main()
{
    if (position.w == 0.0) {
        vs_discard = 1.0;
    } else {
        vs_discard = 0.0;
    }

    //$vec3 colors[$block_type_count$];
    //$$colors[$$block_type_id$$] = $$block_type_name$$;

    //$if (position.w > $block_type_count$ - 1.0) {
        vs_color = colors[0];
    //$} else {
        vs_color = colors[int(position.w)];
    //$}

    gl_Position = vec4(position.xyz, 1.0);
}
