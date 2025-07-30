# Image Archive Viewer

A simple image archive (ZIP) viewer. Open a ZIP file containing images and browse them in a fullscreen mode, with a keyboard- and mouse-friendly user interface.

This archive viewer is built in Python and uses Qt for its user interface.

## Features

- View images from ZIP archives (PNG, JPG)
- Fullscreen view
- Mouse and keyboard navigation
- Zoom and pan with mouse or keyboard

To see help in the application press "H".

## Installation

### Prerequisites

- Python 3.8 or higher

### Dependencies

- PyQt5
- Pillow

### Install from PyPI

To install this tool run:

```
pip install image-archive-viewer
```

Using `uv`:

```
uv pip install image-archive-viewer
```

You can also install it as a `uv` tool and then run it directly from shell:

```
uv tool install image-archive-viewer
```

## Usage

After installation, run the viewer:

```bash
show_images
```

You will be prompted to select a ZIP file containing images. The viewer will open in a fullscreen mode.

## Controls

### Navigation
- **Right Arrow** or **Space**: Next image
- **Left Arrow**: Previous image
- **Q** or **Esc**: Quit

### Zoom
- **+** or **=**: Zoom in
- **-**: Zoom out
- **0**: Reset zoom
- **Mouse wheel**: Zoom in/out

### Panning
- **W**: Pan down
- **S**: Pan up
- **A**: Pan right
- **D**: Pan left
- **Mouse drag**: Pan image (when zoomed in)

### Other
- **H**: Show/hide help information 
- **O**: Open a new ZIP file

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
