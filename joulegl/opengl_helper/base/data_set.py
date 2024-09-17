import abc
from typing import Any, Callable, List, Tuple

from ..vertex_data_handler import OverflowingVertexDataHandler, VertexDataHandler
from .config import ShaderConfig
from .shader import BaseShader


class BaseShaderSet:
    def __init__(
        self, shader: BaseShader, use_func: Callable, element_count_func: Callable
    ) -> None:
        __metaclass__ = abc.ABCMeta
        self.shader: BaseShader = shader
        self.uniform_settings: List[str] = []
        self.use_func: Callable = use_func
        self.element_count_func: Callable = element_count_func

    def set_uniform_label(self, data: List[str]) -> None:
        self.shader.set_uniform_label(data)

    def set_uniform_data(self, data: List[Tuple[str, Any, str]]) -> None:
        self.shader.set_uniform_data(data)

    def set_uniform_labeled_data(self, config: ShaderConfig) -> None:
        self.shader.set_uniform_labeled_data(config)

    @abc.abstractmethod
    def use(self, render: bool = False) -> None:
        raise NotImplementedError


class DefaultSet(BaseShaderSet):
    def __init__(
        self,
        shader: BaseShader,
        data_handler: VertexDataHandler,
        use_func: Callable,
        element_count_func: Callable,
    ) -> None:
        super().__init__(shader, use_func, element_count_func)
        self.data_handler: VertexDataHandler = data_handler

    def use(self, render: bool = False) -> None:
        self.shader.use()
        self.data_handler.set(render)
        self.use_func(self.element_count_func())


class OverflowingSet(BaseShaderSet):
    def __init__(
        self,
        shader: BaseShader,
        data_handler: OverflowingVertexDataHandler,
        use_func: Callable,
        element_count_func: Callable,
    ) -> None:
        super().__init__(shader, use_func, element_count_func)
        self.data_handler: OverflowingVertexDataHandler = data_handler

    def use_sub(self, buffer_index: int = 0, render: bool = False) -> None:
        self.shader.use()
        self.data_handler.set_buffer(buffer_index)
        self.data_handler.set(render)

    def use(self, render: bool = False) -> None:
        self.shader.use()
        for i in range(
            len(
                self.data_handler.targeted_overflowing_buffer_objects[0][
                    0
                ].overflowing_handles
            )
        ):
            self.data_handler.set_buffer(i)
            self.data_handler.set(render)
            self.use_func(self.element_count_func(i), i)


DATA_TO_SET_MAP = {
    VertexDataHandler: DefaultSet,
    OverflowingVertexDataHandler: OverflowingSet,
}
