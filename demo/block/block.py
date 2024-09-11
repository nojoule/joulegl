import os
import sys
from enum import IntEnum
from typing import Callable, Dict, List, Tuple

import numpy as np
from OpenGL.GL import *

sys.path.append(os.getcwd())

from joulegl.opengl_helper.base.config import ShaderConfig
from joulegl.opengl_helper.base.data_set import BaseShaderSet
from joulegl.opengl_helper.base.shader_parser import ShaderParser
from joulegl.opengl_helper.buffer import BufferObject
from joulegl.opengl_helper.render.shader import RenderShaderSetting
from joulegl.opengl_helper.render.utility import (
    OGLRenderFunction,
    generate_render_function,
)
from joulegl.opengl_helper.vertex_data_handler import VertexDataHandler
from joulegl.rendering.renderer import Renderer
from joulegl.utility.app import App
from joulegl.utility.camera import Camera, CameraPose
from joulegl.utility.performance import track_time


class BlockTypes(IntEnum):
    AIR = 0
    DIRT = 1
    SAND = 2
    STONE = 3
    GRASS = 4


class BlockData:
    def __init__(self, pos: np.ndarray, block_type: BlockTypes) -> None:
        self.pos: np.ndarray = pos
        self.block_type = block_type
        self.data = [self.pos[0], self.pos[1], self.pos[2], self.block_type.value]


class BlockDataHandler:
    def __init__(self) -> None:
        self.block_data: List[BlockData] = []
        self.block_palette_map: Dict[int, BlockTypes] = dict()
        self.blocks_changed: bool = False
        self.size: Tuple[int, int, int] = (0, 0, 0)
        self.data: List[float] = []
        self.buffer: bool = True
        self.buffer: BufferObject = BufferObject()

    def get_buffer_points(self) -> int:
        return len(self.block_data)

    def parse_to_buffer(self) -> None:
        self.data = [float(value) for block in self.block_data for value in block.data]
        self.buffer = BufferObject()
        self.buffer.load(np.array(self.data, dtype=np.float32))

    def apply(self, size: Tuple[int, int, int], field: List[BlockData]) -> None:
        self.blocks_changed = True
        self.size = (size[0], size[1], size[2])
        self.block_data = field
        self.parse_to_buffer()


class BlockRenderer(Renderer):
    def __init__(self, bdh: BlockDataHandler) -> None:
        shader_parser: ShaderParser = ShaderParser()
        shader_parser.set_static({"block_type_count": 5})
        shader_parser.set_dynamic(
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
                }
            }
        )
        super().__init__(shader_parser=shader_parser)

        self.bdh = bdh

        shader_settings: List[RenderShaderSetting] = []
        shader_settings.extend(
            [
                RenderShaderSetting(
                    "block",
                    [
                        "block_impostor.vert",
                        "dual_light.frag",
                        "point_to_block_impostor.geom",
                    ],
                    ["screen_width", "screen_height"],
                )
            ]
        )
        self.set_shader(shader_settings)

        self.data_handler: VertexDataHandler = VertexDataHandler([(self.bdh.buffer, 0)])

        def generate_element_count_func(bdh: BlockDataHandler) -> Callable:
            def element_count_func() -> int:
                return bdh.get_buffer_points()

            return element_count_func

        self.execute_funcs["block"] = generate_render_function(
            OGLRenderFunction.ARRAYS, GL_POINTS, depth_test=True
        )
        self.element_count_funcs["block"] = generate_element_count_func(self.bdh)
        self.create_sets(self.data_handler, "block")

    def render(
        self, set_name: str, cam: Camera, config: ShaderConfig | None = None
    ) -> None:
        current_set: BaseShaderSet = self.sets[set_name]
        current_set.set_uniform_data(
            [("projection", cam.projection, "mat4"), ("view", cam.view, "mat4")]
        )
        current_set.set_uniform_labeled_data(config)
        current_set.use(True)

    def delete(self) -> None:
        self.data_handler.delete()


class BlockApp(App):
    def __init__(self) -> None:
        super().__init__("Block Demo")
        self.window.cam.update_base(np.array([5.0, 5.0, 5.0], dtype=np.float32))
        size: Tuple[int, int, int] = (10, 10, 10)
        blocks: List[BlockData] = []
        for x in range(size[0]):
            sqr_off_x = abs(x - 5) * abs(x - 5)
            for y in range(size[1]):
                sqr_off_y = abs(y - 5) * abs(y - 5)
                for z in range(size[2]):
                    if sqr_off_x + sqr_off_y + abs(z - 5) * abs(z - 5) <= 10.0:
                        if y > 6:
                            blocks.append(
                                BlockData(
                                    np.array([x, y, z], dtype=np.float32),
                                    BlockTypes.GRASS,
                                )
                            )
                        else:
                            if y > 4:
                                blocks.append(
                                    BlockData(
                                        np.array([x, y, z], dtype=np.float32),
                                        BlockTypes.DIRT,
                                    )
                                )
                            else:
                                blocks.append(
                                    BlockData(
                                        np.array([x, y, z], dtype=np.float32),
                                        BlockTypes.STONE,
                                    )
                                )

        self.bdh: BlockDataHandler = BlockDataHandler()
        self.bdh.apply(size, blocks)
        self.br: BlockRenderer = BlockRenderer(self.bdh)
        self.br_config: ShaderConfig = ShaderConfig()

        self.set_cam(np.array([5.0, 5.0, 5.0], dtype=np.float32), 10.0, CameraPose.LEFT)

    @track_time(app_name="Block Demo")
    def render(self) -> None:
        self.br.render("block", self.window.cam, self.br_config)


if __name__ == "__main__":
    app = BlockApp()
    app.run()
