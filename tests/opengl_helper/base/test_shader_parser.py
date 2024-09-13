import pytest

from joulegl.opengl_helper.base.shader_parser import ShaderParser, get_shader_src


def test_get_shader_src() -> None:
    shader_src = get_shader_src("tests/shader/test_shader_parser.vert")
    assert "void main()" in shader_src


@pytest.mark.parametrize("unused_group", [True, False])
def test_shader_parser(unused_group: bool) -> None:
    parser = ShaderParser()
    parser.set_static({"block_type_count": 5})
    dynamic_group_rules = {
        "block_type": {
            "id": ["0", "1", "2", "3", "4"],
            "name": [
                "block_default",
                "block_dirt",
                "block_sand",
                "block_stone",
                "block_grass",
            ],
            "r": ["1.0", "0.457", "0.895", "0.6", "0.44"],
            "g": ["1.0", "0.324", "0.867", "0.6", "0.633"],
            "b": ["1.0", "0.22", "0.656", "0.6", "0.277"],
        }
    }
    if unused_group:
        dynamic_group_rules["unused_group"] = {"name": ["test"]}
    parser.set_dynamic(dynamic_group_rules)

    parsed_shader = parser.parse("tests/shader/test_shader_parser.vert")
    assert "const vec3 block_default = vec3(1.0, 1.0, 1.0);" in parsed_shader
    assert "const vec3 block_sand = vec3(0.895, 0.867, 0.656);" in parsed_shader
    assert "const vec3 block_grass = vec3(0.44, 0.633, 0.277);" in parsed_shader


def test_shader_parser_no_config() -> None:
    parser = ShaderParser()
    parser.parse("tests/shader/screen_quad.frag")
    assert True


def test_shader_parser_missing_config() -> None:
    parser = ShaderParser()
    parser.parse("tests/shader/test_shader_parser.vert")
    assert True


def test_shader_parser_ill_config() -> None:
    parser = ShaderParser()
    parser.set_static({"block_type_count": 5})

    with pytest.raises(Exception) as e:
        parser.set_dynamic(
            {
                "block_type": {
                    "id": ["0", "1", "2", "3"],
                    "name": [
                        "block_default",
                        "block_dirt",
                        "block_sand",
                        "block_stone",
                        "block_grass",
                    ],
                    "r": ["1.0", "0.457", "0.895", "0.6", "0.44"],
                    "g": ["1.0", "0.324", "0.867", "0.6", "0.633"],
                    "b": ["1.0", "0.22", "0.656", "0.6", "0.277"],
                }
            }
        )
    assert "Mismatching shader var group size for value" in str(e.value)


def test_shader_parser_ill_file() -> None:
    parser = ShaderParser()
    parser.set_static({"block_type_count": 5})
    parser.set_dynamic(
        {
            "block_type": {
                "id": ["0", "1", "2", "3", "4"],
                "name": [
                    "block_default",
                    "block_dirt",
                    "block_sand",
                    "block_stone",
                    "block_grass",
                ],
                "r": ["1.0", "0.457", "0.895", "0.6", "0.44"],
                "g": ["1.0", "0.324", "0.867", "0.6", "0.633"],
                "b": ["1.0", "0.22", "0.656", "0.6", "0.277"],
            },
            "block_type2": {"name": ["test"]},
        }
    )

    with pytest.raises(Exception) as e:
        parser.parse("tests/shader/test_shader_parser_error.vert")
    assert "Can't replace multiple dynamic variables in danymic shader src" in str(
        e.value
    )
