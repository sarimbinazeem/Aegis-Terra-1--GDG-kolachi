
"""
AI service.

Runs YOLO object detection and returns
structured detection dictionaries.

Important:
YOLO detections are generic visual detections unless
a crop-specific trained model is supplied.

Crop health is still calculated separately using ExG.
"""

import logging

from app.ai.detector import detect_objects

logger = logging.getLogger(__name__)


def analyze_image(
    image_path: str,
) -> list[dict]:
    """
    Run YOLO object detection and return structured detections.

    If YOLO fails, return an empty list instead of destroying
    the entire crop analysis.

    Crop health remains independently calculated using ExG.
    """

    try:
        return detect_objects(
            image_path=image_path
        )

    except Exception:
        logger.exception(
            "YOLO analysis failed for %s",
            image_path,
        )

        return []

