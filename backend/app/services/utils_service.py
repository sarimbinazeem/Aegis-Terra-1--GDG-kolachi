"""
Utility helpers.
"""

from datetime import UTC, datetime


def get_timestamp() -> str:
    """
    Return current UTC timestamp in ISO-8601 format.
    """

    return datetime.now(UTC).isoformat()


def calculate_overall_health(
    cells,
) -> float:
    """
    Calculate percentage of healthy cells.
    """

    if not cells:
        return 0.0

    healthy = sum(
        1
        for cell in cells
        if cell.get("status") == "healthy"
    )

    return round(
        (healthy / len(cells)) * 100,
        2,
    )