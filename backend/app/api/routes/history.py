from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)

from app.services.database_service import (
    get_analysis,
    get_history,
)


router = APIRouter()


@router.get(
    "/history",
    tags=["History"],
)
def history(
    db: Session = Depends(get_db),
):
    """
    Return previous farm analyses.
    """

    analyses = get_history(db)

    return [
        {
            "id": analysis.id,

            "date": (
                analysis.timestamp.isoformat()
                if analysis.timestamp
                else None
            ),

            "health": (
                analysis.overall_health_pct
            ),

            "plots": len(
                analysis.cells
            ),

            "issues": len(
                analysis.alerts
            ),
        }

        for analysis in analyses
    ]


@router.get(
    "/history/{analysis_id}",
    tags=["History"],
)
def history_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    """
    Return one complete stored analysis.
    """

    analysis = get_analysis(
        db,
        analysis_id,
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    return {
        "analysis_id": analysis.id,

        "farm_id": analysis.farm_id,

        "timestamp": (
            analysis.timestamp.isoformat()
            if analysis.timestamp
            else None
        ),

        "overall_health_pct": (
            analysis.overall_health_pct
        ),

        "cells": [
            {
                "id": cell.cell_id,
                "row": cell.row,
                "col": cell.col,
                "status": cell.status,
                "severity": cell.severity,
                "confidence": cell.confidence,
                "exg_value": cell.exg_value,
                "issue": cell.issue,
                "recommended_action": (
                    cell.recommended_action
                ),
            }

            for cell in analysis.cells
        ],

        "alerts": [
            {
                "cell": alert.cell,
                "severity": alert.severity,
                "message": alert.message,
                "action": alert.action,
            }

            for alert in analysis.alerts
        ],

        "detections": [
            {
                "class_id": detection.class_id,

                "class": detection.class_name,

                "confidence": (
                    detection.confidence
                ),

                "bbox": [
                    detection.bbox_x1,
                    detection.bbox_y1,
                    detection.bbox_x2,
                    detection.bbox_y2,
                ],
            }

            for detection in analysis.detections
        ],
    }