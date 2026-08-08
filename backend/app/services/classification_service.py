"""
Crop health classification.

Single source of truth for crop status.

Allowed statuses:
    healthy
    dry
    disease
    pest

The current system primarily uses ExG.
Disease/pest statuses are only produced when
a future agricultural YOLO model provides
corresponding class labels.
"""

from typing import Any


VALID_STATUSES = {
    "healthy",
    "dry",
    "disease",
    "pest",
}


def classify_health(
    average_exg: float,
    detections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Classify crop health from ExG and optional detections.
    """

    detections = detections or []

    # Detection evidence gets priority only when
    # an agricultural model actually provides it.
    if _contains_disease(detections):
        return {
            "status": "disease",
            "severity": "high",
            "message": (
                "Possible disease detected. "
                "Inspect affected plants."
            ),
        }

    if _contains_pest(detections):
        return {
            "status": "pest",
            "severity": "high",
            "message": (
                "Possible pest activity detected. "
                "Inspect the affected area."
            ),
        }

    # ExG-based vegetation classification.
    if average_exg >= 80:
        return {
            "status": "healthy",
            "severity": "low",
            "message": "Crop vegetation appears healthy.",
        }

    if average_exg >= 50:
        return {
            "status": "dry",
            "severity": "medium",
            "message": (
                "Vegetation is below the healthy range. "
                "Possible water or nutrient stress."
            ),
        }

    if average_exg >= 20:
        return {
            "status": "dry",
            "severity": "high",
            "message": (
                "Low vegetation signal detected. "
                "Inspection and irrigation are recommended."
            ),
        }

    return {
        "status": "dry",
        "severity": "urgent",
        "message": (
            "Very low vegetation signal detected. "
            "Immediate field inspection is recommended."
        ),
    }


def _contains_disease(
    detections: list[dict[str, Any]],
) -> bool:
    """
    Check whether an agricultural detection model
    returned a disease-related class.
    """

    keywords = {
        "disease",
        "blight",
        "rust",
        "mildew",
        "fungus",
        "fungal",
        "lesion",
        "spot",
    }

    return _contains_keyword(
        detections,
        keywords,
    )


def _contains_pest(
    detections: list[dict[str, Any]],
) -> bool:
    """
    Check whether an agricultural detection model
    returned a pest-related class.
    """

    keywords = {
        "pest",
        "aphid",
        "caterpillar",
        "insect",
        "beetle",
        "locust",
        "worm",
        "mite",
    }

    return _contains_keyword(
        detections,
        keywords,
    )


def _contains_keyword(
    detections: list[dict[str, Any]],
    keywords: set[str],
) -> bool:

    for detection in detections:

        label = str(
            detection.get(
                "class",
                detection.get(
                    "class_name",
                    "",
                ),
            )
        ).lower()

        if any(
            keyword in label
            for keyword in keywords
        ):
            return True

    return False