# src/visualization/utils.py

import numpy as np


def get_diverging_color(value, vmin=-0.2, vmax=0.2):
    """
    Convert a policy_effect value into a color.
    Red  -> negative impact
    White -> neutral
    Green -> positive impact

    Parameters
    ----------
    value : float
        Policy effect value
    vmin : float
        Minimum expected value
    vmax : float
        Maximum expected value

    Returns
    -------
    str
        HEX color code
    """

    # Clip values to avoid extreme outliers breaking the color scale
    value = max(min(value, vmax), vmin)

    # Normalize value to [0, 1]
    norm = (value - vmin) / (vmax - vmin)

    # Red → White → Green interpolation
    if norm < 0.5:
        # Red to White
        r = 255
        g = int(2 * norm * 255)
        b = int(2 * norm * 255)
    else:
        # White to Green
        r = int(2 * (1 - norm) * 255)
        g = 255
        b = int(2 * (1 - norm) * 255)

    return f"#{r:02x}{g:02x}{b:02x}"
