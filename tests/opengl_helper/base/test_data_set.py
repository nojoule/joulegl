from unittest.mock import Mock

from joulegl.opengl_helper.base.config import ShaderConfig
from joulegl.opengl_helper.base.data_set import (
    DATA_TO_SET_MAP,
    BaseShaderSet,
    DefaultSet,
    OverflowingSet,
)
from joulegl.opengl_helper.base.shader import BaseShader
from joulegl.opengl_helper.vertex_data_handler import (
    OverflowingVertexDataHandler,
    VertexDataHandler,
)


def test_base_shader_set_initialization():
    shader = Mock(spec=BaseShader)
    use_func = Mock()
    element_count_func = Mock()
    base_shader_set = BaseShaderSet(shader, use_func, element_count_func)

    assert base_shader_set.shader == shader
    assert base_shader_set.use_func == use_func
    assert base_shader_set.element_count_func == element_count_func


def test_base_shader_set_set_uniform_label():
    shader = Mock(spec=BaseShader)
    base_shader_set = BaseShaderSet(shader, Mock(), Mock())
    data = ["label1", "label2"]

    base_shader_set.set_uniform_label(data)
    shader.set_uniform_label.assert_called_once_with(data)


def test_base_shader_set_set_uniform_data():
    shader = Mock(spec=BaseShader)
    base_shader_set = BaseShaderSet(shader, Mock(), Mock())
    data = [("label1", 1, "type1"), ("label2", 2, "type2")]

    base_shader_set.set_uniform_data(data)
    shader.set_uniform_data.assert_called_once_with(data)


def test_base_shader_set_set_uniform_labeled_data():
    shader = Mock(spec=BaseShader)
    base_shader_set = BaseShaderSet(shader, Mock(), Mock())
    config = Mock(spec=ShaderConfig)

    base_shader_set.set_uniform_labeled_data(config)
    shader.set_uniform_labeled_data.assert_called_once_with(config)


def test_default_set_initialization():
    shader = Mock(spec=BaseShader)
    data_handler = Mock(spec=VertexDataHandler)
    use_func = Mock()
    element_count_func = Mock()
    default_set = DefaultSet(shader, data_handler, use_func, element_count_func)

    assert default_set.shader == shader
    assert default_set.data_handler == data_handler
    assert default_set.use_func == use_func
    assert default_set.element_count_func == element_count_func


def test_default_set_use():
    shader = Mock(spec=BaseShader)
    data_handler = Mock(spec=VertexDataHandler)
    use_func = Mock()
    element_count_func = Mock(return_value=5)
    default_set = DefaultSet(shader, data_handler, use_func, element_count_func)

    default_set.use(render=True)
    shader.use.assert_called_once()
    data_handler.set.assert_called_once_with(True)
    use_func.assert_called_once_with(5)


def test_overflowing_set_initialization():
    shader = Mock(spec=BaseShader)
    data_handler = Mock(spec=OverflowingVertexDataHandler)
    use_func = Mock()
    element_count_func = Mock()
    overflowing_set = OverflowingSet(shader, data_handler, use_func, element_count_func)

    assert overflowing_set.shader == shader
    assert overflowing_set.data_handler == data_handler
    assert overflowing_set.use_func == use_func
    assert overflowing_set.element_count_func == element_count_func


def test_overflowing_set_use_sub():
    shader = Mock(spec=BaseShader)
    data_handler = Mock(spec=OverflowingVertexDataHandler)
    use_func = Mock()
    element_count_func = Mock()
    overflowing_set = OverflowingSet(shader, data_handler, use_func, element_count_func)

    overflowing_set.use_sub(buffer_index=1, render=True)
    shader.use.assert_called_once()
    data_handler.set_buffer.assert_called_once_with(1)
    data_handler.set.assert_called_once_with(True)


def test_overflowing_set_use():
    shader = Mock(spec=BaseShader)
    data_handler = Mock(spec=OverflowingVertexDataHandler)
    data_handler.targeted_overflowing_buffer_objects = [
        [Mock(overflowing_handles=[1, 2, 3])]
    ]
    use_func = Mock()
    element_count_func = Mock()
    overflowing_set = OverflowingSet(shader, data_handler, use_func, element_count_func)

    overflowing_set.use(render=True)
    shader.use.assert_called_once()
    assert data_handler.set_buffer.call_count == 3
    assert data_handler.set.call_count == 3
    assert use_func.call_count == 3


def test_data_to_set_map():
    assert DATA_TO_SET_MAP[VertexDataHandler] == DefaultSet
    assert DATA_TO_SET_MAP[OverflowingVertexDataHandler] == OverflowingSet
