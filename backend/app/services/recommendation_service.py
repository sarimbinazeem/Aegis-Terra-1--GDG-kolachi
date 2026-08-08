"""
Recommendation engine.

Converts the final crop status into a practical
farmer-facing recommendation.
"""

from typing import Any


def generate_recommendation(
    classification: dict[str, Any],
    exg_value: float | None = None,
    detections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:

    status = classification["status"]
    severity = classification["severity"]

    detections = detections or []

    confidence = calculate_confidence(
        status=status,
        severity=severity,
        exg_value=exg_value,
        detection_count=len(detections),
    )

    recommendations = {
        "healthy": {
            "issue": "",
            "recommended_action": (
                "No immediate action required. "
                "Continue regular monitoring."
            ),
        },

        "dry": {
            "issue": (
                "Low vegetation signal detected; "
                "possible water or nutrient stress."
            ),
            "recommended_action": (
                "Inspect soil moisture and irrigation. "
                "Irrigate the affected area if needed."
            ),
        },

        "disease": {
            "issue": (
                "Possible disease-related visual "
                "pattern detected."
            ),
            "recommended_action": (
                "Inspect affected plants closely. "
                "Confirm the disease before applying "
                "an appropriate treatment."
            ),
        },

        "pest": {
            "issue": (
                "Possible pest activity detected."
            ),
            "recommended_action": (
                "Inspect the affected area for pests "
                "and apply appropriate pest control "
                "if infestation is confirmed."
            ),
        },
    }

    recommendation = recommendations.get(
        status,
        {
            "issue": "Unknown crop condition.",
            "recommended_action": (
                "Inspect the affected area manually."
            ),
        },
    )

    return {
        "status": status,
        "severity": severity,
        "confidence": confidence,
        "issue": recommendation["issue"],
        "recommended_action": (
            recommendation[
                "recommended_action"
            ]
        ),
    }


def calculate_confidence(
    status: str,
    severity: str,
    exg_value: float | None,
    detection_count: int,
) -> float:
    """
    Estimate confidence from available evidence.

    This is NOT a machine-learning probability.
    It is a rule-based confidence indicator.
    """

    if status in {"disease", "pest"}:

        if detection_count >= 3:
            return 0.95

        if detection_count == 2:
            return 0.90

        if detection_count == 1:
            return 0.85

        return 0.50

    if exg_value is None:
        return 0.50

    if status == "healthy":

        if exg_value >= 120:
            return 0.95

        if exg_value >= 100:
            return 0.90

        return 0.80

    # Dry / stress classification.
    if exg_value < 20:
        return 0.95

    if exg_value < 50:
        return 0.90

    return 0.80