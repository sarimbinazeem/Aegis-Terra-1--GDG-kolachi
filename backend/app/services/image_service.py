"""
Image service.

Responsible for loading uploaded images with OpenCV and
extracting basic image metadata.
"""

import cv2
import numpy as np


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image from disk using OpenCV.

    Raises:
        ValueError: If the image cannot be loaded.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    return image


def get_image_info(image: np.ndarray) -> dict[str, int]:
    """
    Return basic information about an OpenCV image.
    """

    if image is None:
        raise ValueError("Image cannot be None.")

    if len(image.shape) != 3:
        raise ValueError("Expected a color image with 3 channels.")

    height, width, channels = image.shape

    return {
        "width": int(width),
        "height": int(height),
        "channels": int(channels),
    }