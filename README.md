# pbrtpy

## About
A Python subset of [pbrt-v2](https://github.com/mmp/pbrt-v2) focussing only on geometry (i.e. no materials are currently supported).

## Use
<p align="center"><img src="https://github.com/matt77hias/pbrtpy/blob/master/res/pbrtpy.png" width="430"><img src="https://github.com/matt77hias/pbrtpy/blob/master/res/Wireframe Film.png" width="430"></p>

```python
from pbrtpy import test

test()
```

## Extra Features
* Basic .obj parser
* Scene generators
* Multi Film support: <code>MultiFilm</code>
* False Color support (good for debugging and optimizing): <code>FalseColorFilm</code>
* Wireframe Rendering (good for debugging): <code>WireframeRenderer</code> and <code>WireframeFilm</code>
