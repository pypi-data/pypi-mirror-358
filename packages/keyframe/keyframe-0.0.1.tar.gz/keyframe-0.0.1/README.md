# KeyFrame
A simple yet powerful animation timeline engine for Python.
---
## Installation
```bash
pip install keyframe
```
## Example
```python
from keyframe import Scene
scene = Scene(duration=3, bg_color="#111111", size=(720, 480), fps=30)
scene.render("keyframe.mp4")
```