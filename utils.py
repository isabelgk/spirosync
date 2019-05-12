import colorsys

import numpy as np


def generate_sub_palette(rgb, num_colors=16):
    """
    From one input color, create a list of colors (a sub-palette) close to that original.

    :param rgb: An RGB tuple as an initializer color
    :param num_colors: integer number of colors in output palette
    :return: list of RGB tuples of length num_colors
    """
    # Convert from RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(*rgb)

    vs = np.linspace(0.7, 1.0, num_colors)
    ss = np.linspace(0.01, 1.0, num_colors)

    palette = [colorsys.hsv_to_rgb(h, ss[i], vs[i]) for i in range(num_colors)]

    return palette


def centroid(points):
    """Calculate the centroid of a list of (x, y) tuples."""
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    _len = len(points)
    centroid_x = sum(x_coords)/_len
    centroid_y = sum(y_coords)/_len
    return [centroid_x, centroid_y]
