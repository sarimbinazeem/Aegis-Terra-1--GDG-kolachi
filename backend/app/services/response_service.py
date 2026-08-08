"""
Build the final API response.
"""

from app.services.utils_service import (
    get_timestamp,
    calculate_overall_health,
)


def build_response(
    grid,
    detections,
    alerts,
):
    """
    Build the frontend-facing analysis response.
    """

    return {
        "farm_id": "AT1-DEMO",

        "timestamp": get_timestamp(),

        "overall_health_pct": (
            calculate_overall_health(grid)
        ),

        "grid": {
            "rows": 4,
            "cols": 4,
            "cell_size_m": 10,
        },

        "cells": grid,

        "detections": detections,

        "alerts": alerts,
    }