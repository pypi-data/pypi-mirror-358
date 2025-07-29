# SpectraSketch

**SpectraSketch** is a flexible Python drawing library built on top of OpenCV. It enables developers, students, and hobbyists to create and manipulate custom geometric shapes programmatically with ease. It also supports undo/redo functionality, shape rotation, filled or outlined styles, and batch drawing operations.

##  Features

- Draw a variety of shapes - lines, rectangles, circles, triangles, diamonds, polygons, stars, hearts and more
- Rotate shapes with precise angle control
- Undo/Redo support for safe experimentation
- Customisable canvas size and background color
- Batch mode for grouped drawing operations
- Input validation to prevent drawing errors
- Save your canvas as an image (PNG,JPG etc.)
- Simple API that integrates easily into other python projects

##  Installation

```bash
pip install spectrasketch
```

## Quick Example

```python
from spectrasketch import ShapeLab

lab = ShapeLab(width=800, height=600, background_color=(255, 255, 255))
lab.line((50, 50), (200, 50), (255, 0, 0), 2)
lab.rectangle((100, 100), (250, 200), 45, (0, 255, 0), 3)
lab.circle((400, 300), 50, (0, 0, 255), -1)
lab.launch_viewer()
```

## Why SpectraSketch?

- Fast prototyping for Computer Vision projects
- Create educational visualisations for geometry or graphics
- Develop custom image annotation tools
- Easily extend for your own shapes and logic

## License

Licensed under the Apache License, Version 2.0


