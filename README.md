[![License][s1]][li]

[s1]: https://img.shields.io/badge/licence-GPL%203.0-blue.svg
[li]: https://raw.githubusercontent.com/matt77hias/pbrtpy/master/LICENSE.txt

# pbrtpy

## About
A Python subset of [pbrt-v2](https://github.com/mmp/pbrt-v2) focussing only on geometry (i.e. no materials for surfaces and volumes are currently supported).

## Use
<p align="center">
<img src="res/pbrtpy.png" width="430">
<img src="res/Wireframe Film.png" width="430">
</p>

```python
from pbrtpy import test

test()
```

## Extra Features
* Basic .obj parser
* Scene generators
* Multi Film support: `MultiFilm`
* False Color support (good for debugging and optimizing): `FalseColorFilm`
* Wireframe Rendering (good for debugging): `WireframeRenderer` and `WireframeFilm`
