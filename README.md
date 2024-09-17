# JouleGL
Low level rendering framework using OpenGL python bindings. For feedback or questions, feel free to join my stream and community at https://www.twitch.tv/nojoule .

## Test Coverage
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/julrog/track_work/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-87%25-brightgreen.svg" /></a>
<!-- Pytest Coverage Comment:End -->

## Installation

Install using pip:
```Shell
pip install -r requirements.txt
```

## Usage

Clone this repo and look in the [demo](./demo) folder for examples.

### Demo: Balls
Showing compute shader applying noise to vertex positions with dynamic use of two different shader for basic triangles or more complex geometry shader.

```Shell
python demo/balls/balls.py
```

![balls, triangle connections between random positions](./docs/balls_demo.png)
![balls, random positions rendered as spheres](./docs/balls_demo_2.png)

### Demo: Block
Showcasing dynamic shader generation.

```Shell
python demo/block/block.py
```

![block, positions rendered as cubes, with varying color and shading](./docs/block_demo.png)