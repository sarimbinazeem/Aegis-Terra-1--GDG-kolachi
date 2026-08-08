"""
Excess Green Index (ExG) analysis.

ExG = 2G - R - B
"""

import numpy as np


def calculate_exg(image):
    """
    Calculate Excess Green Index.
    """

    if image is None:
        raise ValueError(
            "Cannot calculate ExG from an empty image."
        )

    if image.ndim != 3 or image.shape[2] < 3:
        raise ValueError(
            "Expected a 3-channel image."
        )

    blue = image[:, :, 0].astype(
        np.float32
    )

    green = image[:, :, 1].astype(
        np.float32
    )

    red = image[:, :, 2].astype(
        np.float32
    )

    return (
        (2 * green)
        - red
        - blue
    )


def summarize_exg(exg):
    """
    Return ExG statistics.
    """

    if exg.size == 0:
        raise ValueError(
            "Cannot summarize an empty ExG matrix."
        )

    return {
        "minimum": float(
            exg.min()
        ),

        "maximum": float(
            exg.max()
        ),

        "average": float(
            exg.mean()
        ),
    }