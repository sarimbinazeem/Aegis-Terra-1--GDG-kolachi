from datetime import datetime, UTC
from app.database.database import analyses_collection


async def save_analysis(analysis: dict) -> str:
    """
    Save a completed crop analysis to MongoDB.
    """

    document = {
        **analysis,
        "created_at": datetime.now(UTC),
    }

    result = await analyses_collection.insert_one(document)

    return str(result.inserted_id)


async def get_analysis_history(limit: int = 50):
    """
    Return recent crop analyses for the History screen.
    """

    cursor = (
        analyses_collection
        .find({})
        .sort("created_at", -1)
        .limit(limit)
    )

    history = []

    async for document in cursor:
        document["_id"] = str(document["_id"])

        history.append({
            "id": document["_id"],
            "farm_id": document.get("farm_id"),
            "timestamp": document.get("timestamp"),
            "overall_health_pct": document.get("overall_health_pct"),
            "grid": document.get("grid"),
            "cells": document.get("cells", []),
            "alerts": document.get("alerts", []),
            "detections": document.get("detections", []),
        })

    return history


async def get_analysis_by_id(analysis_id: str):
    """
    Return one historical analysis.
    """

    from bson import ObjectId

    document = await analyses_collection.find_one(
        {"_id": ObjectId(analysis_id)}
    )

    if not document:
        return None

    document["_id"] = str(document["_id"])

    return document