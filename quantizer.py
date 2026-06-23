"""
quantize.py

Dither + quantize an image to a fixed predefined palette
using Floyd-Steinberg error diffusion.
"""

from PIL import Image
import numpy as np
from scipy.spatial import cKDTree

from common import Color, JoPColor


def quantize(image: Image.Image, palette: dict[Color, JoPColor]) -> list[list[JoPColor]]:
    """
    Dither and quantize `image` to the colors in `palette`.

    image:   PIL Image (any mode, converted to RGB internally)
    palette: dict[Color, JoPColor] — Color keys have .r .g .b as 0-255 ints
    returns: 2D list result[y][x] of JoPColor
    """
    arr = np.array(image.convert("RGB"), dtype=np.float64)  # (H, W, 3)
    h, w = arr.shape[:2]

    # build KDTree from palette — handles any palette size from 16 to 16M
    colors = list(palette.keys())
    palette_arr = np.array([(c.r, c.g, c.b) for c in colors], dtype=np.float64)  # (N, 3)
    tree = cKDTree(palette_arr)

    buf = arr.copy()
    result = [[None] * w for _ in range(h)]

    for y in range(h):
        for x in range(w):
            old = np.clip(buf[y, x], 0, 255)
            _, idx = tree.query(old)
            result[y][x] = palette[colors[idx]]
            error = old - palette_arr[idx]

            # Atkinson dithering — only propagates 6/8 of error, discards the rest.
            # Solid colors stay solid; dithering only appears on genuine transitions.
            e = error / 8
            if x + 1 < w:
                buf[y,     x + 1] += e
            if x + 2 < w:
                buf[y,     x + 2] += e
            if y + 1 < h:
                if x - 1 >= 0:
                    buf[y + 1, x - 1] += e
                buf[y + 1, x    ] += e
                if x + 1 < w:
                    buf[y + 1, x + 1] += e
            if y + 2 < h:
                buf[y + 2, x    ] += e

    return result