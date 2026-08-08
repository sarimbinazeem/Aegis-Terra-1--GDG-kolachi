"""
Quick smoke test for Aegis-Terra intelligence layer.

Run from backend:

    python test_intelligence.py

This test does not require internet access.
"""

from app.intelligence import (
    init_db,
    seed_knowledge_base,
    get_crop,
    get_soil,
    build_recommendation,
    farmer_message,
)


def main():
    init_db()
    seed_knowledge_base()

    crop = get_crop("Wheat")
    assert crop is not None
    assert crop["name"] == "Wheat"

    soil = get_soil(24.8607, 67.0011)
    assert soil["region"] == "karachi"

    farm = {
        "farm_id": "AT1-DEMO",
        "name": "Demo Farm",
        "crop": "Wheat",
        "language": "English",
    }

    analysis = {
        "overall_health_pct": 68,
        "overall_status": "Needs Attention",
        "cells": [
            {"id": "A1", "status": "healthy"},
            {"id": "B3", "status": "dry"},
        ],
    }

    weather = {
        "temperature_c": 36,
        "humidity_pct": 30,
        "rainfall_mm": 0,
    }

    recommendation = build_recommendation(
        farm=farm,
        analysis=analysis,
        weather=weather,
        soil=soil,
    )

    assert recommendation["possible_cause"]
    assert recommendation["confidence_pct"] > 0
    assert recommendation["recommended_action"]

    print("Phase 3-10 intelligence smoke test: PASSED")
    print("Crop:", crop["name"])
    print("Soil:", soil["name"])
    print("Cause:", recommendation["possible_cause"])
    print("Confidence:", recommendation["confidence_pct"])
    print("Action:", recommendation["recommended_action"])
    print("Farmer message:", farmer_message(recommendation, "English"))


if __name__ == "__main__":
    main()
