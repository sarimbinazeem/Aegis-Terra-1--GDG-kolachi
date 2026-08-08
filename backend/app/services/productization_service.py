"""
Phase 10 productization intelligence.

Provides:
- before/after comparison
- deterioration detection
- rescan recommendations
- confidence summary
- expert escalation
"""

from datetime import datetime, timedelta


def calculate_average_confidence(analysis) -> float:
    """
    Calculate average confidence across analyzed cells.
    """

    cells = analysis.cells

    if not cells:
        return 0.0

    confidence = sum(
        float(cell.confidence or 0)
        for cell in cells
    )

    return round(
        confidence / len(cells),
        3,
    )


def calculate_deterioration(
    current,
    previous,
) -> dict:
    """
    Compare current analysis against the previous
    analysis for the same farm.
    """

    if previous is None:
        return {
            "available": False,
            "health_change": 0,
            "deteriorated": False,
            "message": "No previous scan available.",
        }

    current_health = float(
        current.overall_health_pct or 0
    )

    previous_health = float(
        previous.overall_health_pct or 0
    )

    change = round(
        current_health - previous_health,
        2,
    )

    deteriorated = change <= -10

    if deteriorated:
        message = (
            f"Farm health decreased by "
            f"{abs(change):.1f}% since the previous scan."
        )
    elif change >= 10:
        message = (
            f"Farm health improved by "
            f"{change:.1f}% since the previous scan."
        )
    else:
        message = (
            "Farm health is relatively stable "
            "compared with the previous scan."
        )

    return {
        "available": True,
        "health_change": change,
        "previous_health": previous_health,
        "current_health": current_health,
        "deteriorated": deteriorated,
        "message": message,
    }


def build_productization_summary(
    current,
    previous=None,
) -> dict:
    """
    Build the complete Phase 10 summary.
    """

    confidence = calculate_average_confidence(
        current
    )

    comparison = calculate_deterioration(
        current,
        previous,
    )

    health = float(
        current.overall_health_pct or 0
    )

    urgent_alerts = sum(
        1
        for alert in current.alerts
        if alert.severity == "urgent"
    )

    expert_escalation = (
        health < 45
        or urgent_alerts > 0
        or confidence < 0.50
    )

    rescan_hours = 24

    if health >= 85:
        rescan_hours = 48
    elif health >= 70:
        rescan_hours = 36

    next_scan = (
        datetime.utcnow()
        + timedelta(hours=rescan_hours)
    )

    return {
        "confidence": confidence,

        "confidence_pct": round(
            confidence * 100,
            1,
        ),

        "comparison": comparison,

        "deterioration_alert": (
            comparison["deteriorated"]
        ),

        "expert_escalation": expert_escalation,

        "expert_reason": (
            "Consider expert/agronomist review."
            if expert_escalation
            else "No expert escalation required."
        ),

        "rescan": {
            "recommended": True,
            "hours": rescan_hours,
            "recommended_at": next_scan.isoformat(),
            "message": (
                f"Rescan the field in approximately "
                f"{rescan_hours} hours."
            ),
        },
    }