# tevclient &nbsp;&nbsp; ![](https://github.com/tom94/tevclient/workflows/CI/badge.svg)

Module for remote-controlling the [tev image viewer](https://github.com/Tom94/tev).
This module implements tev's IPC protocol, allowing you to control tev via a TCP connection.
You can create, modify, reload, and close images as well as overlay vector graphics.

The initial version of this module was written by [Tomáš Iser](https://tomasiser.com/) and contributed to **tev**.

## Installation

```bash
pip install tevclient
```

## Usage

Enter a context via the `Ipc` class (or an async context using `IpcAsync`), which will handle the connection to **tev**.
Then instrument **tev** by calling the various methods of the context.

```python
import tevclient

with tevclient.Ipc() as tev_ipc:
# or: async with tevclient.IpcAsync() as tev_ipc:

    # Open an image
    tev_ipc.open_image("path/to/image.png")
    # or: await tev_ipc.open_image("path/to/image.png")

    # Create a new image
    tev_ipc.create_image("My Image", width=800, height=600, channel_names=["R", "G", "B"])

    # Update the image with pixel data
    import numpy as np
    image_data = np.random.rand(600, 800, 3)  # Random RGB data
    tev_ipc.update_image("My Image", image_data, ["R", "G", "B"])

    # Close the image
    tev_ipc.close_image("My Image")
```

The following methods are available:

| Operation | Function
| :--- | :----------
| `open_image` | Opens an image from a specified path on the machine __tev__ is running on.
| `create_image` | Creates a blank image with a specified name, size, and set of channels. If an image with the specified name already exists, it is overwritten.
| `update_image` | Updates the pixels in a rectangular region.
| `close_image` | Closes a specified image.
| `reload_image` | Reloads an image from a specified path on the machine __tev__ is running on.
| `update_vector_graphics` | Draws vector graphics over a specified image.

Each method comes with type annotations and a docstring, so should be self-explanatory when used in an IDE.

## Examples

More complete examples than the one above can be found in the `examples/` directory of this repository.
Below is an excerpt that showcases tilewise updating of an image and drawing vector graphics over it.

```python
import time
import numpy as np
import tevclient

with tevclient.Ipc() as tev_ipc:
    # Create sample image in one go. The image will have RGB channels (displayed as one layer)
    # as well as a 'Bonus' channel (displayed as another layer)
    image_data = np.full((300, 200, 3), 1.0)
    image_data[40:61, :, 0] = 0.0
    image_data[:, 40:61, 1] = 0.0
    image_data[50:71, 50:71, 2] = 0.0

    bonus_data = image_data[:, :, 0] + image_data[:, :, 1] + image_data[:, :, 2]

    tev_ipc.create_image("Test image 1", width=200, height=300, channel_names=["R", "G", "B", "Bonus"])
    tev_ipc.update_image("Test image 1", image_data, ["R", "G", "B"])
    tev_ipc.update_image("Test image 1", bonus_data, ["Bonus"])

    # Create another image that will be populated over time
    RESOLUTION = 256
    TILE_SIZE = 64
    N_TILES = (RESOLUTION // TILE_SIZE) ** 2

    tev_ipc.create_image("Test image 2", width=RESOLUTION, height=RESOLUTION, channel_names=["R", "G", "B"])

    idx = 0
    for y in range(0, RESOLUTION, TILE_SIZE):
        for x in range(0, RESOLUTION, TILE_SIZE):
            tile = np.full((TILE_SIZE, TILE_SIZE, 3), idx / N_TILES)
            tev_ipc.update_image("Test image 2", tile, ["R", "G", "B"], x, y)

            # Display a rectangle where the tile was updated
            tev_ipc.update_vector_graphics(
                "Test image 2",
                [
                    tevclient.vg_begin_path(),
                    tevclient.vg_rect(x, y, TILE_SIZE, TILE_SIZE),
                    # Alternatively: draw rectangle manually
                    # tevclient.vg_move_to(x, y),
                    # tevclient.vg_line_to(x, y + TILE_SIZE),
                    # tevclient.vg_line_to(x + TILE_SIZE, y + TILE_SIZE),
                    # tevclient.vg_line_to(x + TILE_SIZE, y),
                    # tevclient.vg_close_path(),
                    tevclient.vg_stroke(),
                ],
            )

            idx += 1
            time.sleep(0.1)
```

## License

GPLv3; see [LICENSE](LICENSE.txt) for details.
