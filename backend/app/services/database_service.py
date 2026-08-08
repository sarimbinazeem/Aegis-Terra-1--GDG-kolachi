"""
Database persistence service.

Stores completed crop analyses and retrieves
historical analyses.
"""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import (
    Analysis,
    AnalysisAlert,
    AnalysisCell,
    AnalysisDetection,
)

from app.services.farm_service import (
    get_farm,
)


DEFAULT_FARM_ID = "AT1-DEMO"


def save_analysis(
    db: Session,
    result: dict[str, Any],
    image_filename: str | None = None,
) -> Analysis:
    """
    Save a complete crop analysis.

    Every analysis belongs to a farm profile.
    """

    try:

        farm_id = result.get(
            "farm_id",
            DEFAULT_FARM_ID,
        )

        # -----------------------------------------
        # Make sure the farm exists
        # -----------------------------------------

        farm = get_farm(
            db,
            farm_id,
        )

        if not farm:

            raise ValueError(
                f"Farm '{farm_id}' does not exist."
            )

        # -----------------------------------------
        # Analysis
        # -----------------------------------------

        analysis = Analysis(
            farm_id=farm_id,

            timestamp=_parse_timestamp(
                result.get("timestamp")
            ),

            overall_health_pct=result.get(
                "overall_health_pct",
                0,
            ),

            image_filename=image_filename,
        )

        db.add(analysis)

        db.flush()

        # -----------------------------------------
        # Cells
        # -----------------------------------------

        for cell in result.get(
            "cells",
            [],
        ):

            analysis.cells.append(
                AnalysisCell(
                    cell_id=cell["id"],
                    row=cell["row"],
                    col=cell["col"],
                    status=cell["status"],
                    severity=cell["severity"],
                    confidence=cell["confidence"],
                    exg_value=cell["exg_value"],
                    issue=cell.get(
                        "issue",
                        "",
                    ),
                    recommended_action=cell.get(
                        "recommended_action",
                        "",
                    ),
                )
            )

        # -----------------------------------------
        # Alerts
        # -----------------------------------------

        for alert in result.get(
            "alerts",
            [],
        ):

            analysis.alerts.append(
                AnalysisAlert(
                    cell=alert["cell"],
                    severity=alert["severity"],
                    message=alert["message"],
                    action=alert.get(
                        "action",
                        "",
                    ),
                )
            )

        # -----------------------------------------
        # YOLO detections
        # -----------------------------------------

        for detection in result.get(
            "detections",
            [],
        ):

            bbox = detection.get(
                "bbox",
                [0, 0, 0, 0],
            )

            if len(bbox) != 4:
                bbox = [0, 0, 0, 0]

            analysis.detections.append(
                AnalysisDetection(
                    class_id=detection[
                        "class_id"
                    ],

                    class_name=detection.get(
                        "class",
                        detection.get(
                            "class_name",
                            "unknown",
                        ),
                    ),

                    confidence=detection[
                        "confidence"
                    ],

                    bbox_x1=bbox[0],
                    bbox_y1=bbox[1],
                    bbox_x2=bbox[2],
                    bbox_y2=bbox[3],
                )
            )

        # -----------------------------------------
        # Commit
        # -----------------------------------------

        db.commit()

        db.refresh(
            analysis
        )

        return analysis

    except Exception:

        db.rollback()

        raise


def get_history(
    db: Session,
    farm_id: str = DEFAULT_FARM_ID,
):
    """
    Return historical analyses for a farm.
    """

    return (
        db.query(Analysis)
        .filter(
            Analysis.farm_id == farm_id
        )
        .order_by(
            Analysis.timestamp.desc()
        )
        .all()
    )


def get_analysis(
    db: Session,
    analysis_id: int,
):
    """
    Return one historical analysis.
    """

    return (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id
        )
        .first()
    )


def _parse_timestamp(
    value: str | None,
) -> datetime:

    if not value:
        return datetime.utcnow()

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        ).replace(
            tzinfo=None
        )

    except ValueError:

        return datetime.utcnow()