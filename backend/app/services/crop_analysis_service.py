
"""
Aegis-Terra Unified Crop Analysis Service

Complete crop-analysis pipeline:

IMAGE
  ↓
GRID
  ↓
ExG per cell
  ↓
Cell classification
  ↓
Cell recommendation
  ↓
Alerts
  ↓
YOLO visual detection
  ↓
Overall farm health
  ↓
Database persistence
  ↓
Final response

Important:
ExG is the primary vegetation-health signal.

YOLO detections are an additional visual-detection signal.
A generic YOLO model is NOT treated as a crop-disease model.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.ai.detector import (
    detect_objects,
    get_detector_info,
)

from app.database.models import (
    Analysis,
    AnalysisAlert,
    AnalysisCell,
    AnalysisDetection,
)


# ============================================================
# Configuration
# ============================================================

ROWS = 4
COLS = 4

DEFAULT_CELL_SIZE_M = 1.0


# ============================================================
# ExG thresholds
# ============================================================

# These are heuristic demo thresholds, not scientifically
# calibrated disease thresholds.

EXG_HEALTHY_THRESHOLD = 80
EXG_DRY_THRESHOLD = 50
EXG_CRITICAL_THRESHOLD = 20


# ============================================================
# Image loading
# ============================================================

def load_image(
    image_path: str | Path,
) -> np.ndarray:

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    return image


# ============================================================
# ExG
# ============================================================

def calculate_exg(
    image: np.ndarray,
) -> np.ndarray:

    """
    Calculate Excess Green:

        ExG = 2G - R - B

    OpenCV uses BGR ordering.
    """

    image_float = image.astype(
        np.float32
    )

    blue = image_float[:, :, 0]
    green = image_float[:, :, 1]
    red = image_float[:, :, 2]

    exg = (
        2.0 * green
        - red
        - blue
    )

    return exg


# ============================================================
# Classification
# ============================================================

def classify_exg(
    exg_average: float,
) -> tuple[str, str]:

    """
    Convert ExG into the project's current
    health status/severity vocabulary.

    Status:
        healthy
        dry
        critical

    Severity:
        low
        medium
        high
        urgent
    """

    if exg_average >= EXG_HEALTHY_THRESHOLD:

        return (
            "healthy",
            "low",
        )

    if exg_average >= EXG_DRY_THRESHOLD:

        return (
            "dry",
            "medium",
        )

    if exg_average >= EXG_CRITICAL_THRESHOLD:

        return (
            "dry",
            "high",
        )

    return (
        "critical",
        "urgent",
    )


# ============================================================
# Recommendations
# ============================================================

def recommendation_for_status(
    status: str,
    severity: str,
) -> tuple[str, str]:

    """
    Return:

        issue
        recommended_action

    Recommendations are based on the actual
    classification result.
    """

    if status == "healthy":

        return (
            "No significant vegetation stress detected.",
            "Continue normal crop monitoring and maintain the current irrigation and field-care routine.",
        )

    if status == "dry":

        if severity == "high":

            return (
                "Vegetation signal indicates significant moisture stress.",
                "Inspect this plot for irrigation problems and check soil moisture as soon as possible.",
            )

        return (
            "Vegetation signal indicates possible moisture stress.",
            "Inspect soil moisture and irrigation coverage for this plot.",
        )

    if status == "critical":

        return (
            "Very low vegetation signal detected.",
            "Inspect this plot immediately for severe water stress, crop damage, or other field problems.",
        )

    return (
        "Crop condition requires inspection.",
        "Inspect the plot manually and continue monitoring.",
    )


# ============================================================
# Grid
# ============================================================

def split_into_cells(
    image: np.ndarray,
    rows: int = ROWS,
    cols: int = COLS,
) -> list[
    tuple[
        str,
        int,
        int,
        np.ndarray,
    ]
]:

    """
    Split the image into a regular grid.

    Cell naming:

        A1 A2 A3 A4
        B1 B2 B3 B4
        C1 C2 C3 C4
        D1 D2 D3 D4
    """

    height, width = image.shape[:2]

    cell_height = height / rows
    cell_width = width / cols

    cells = []

    for row_index in range(rows):

        for col_index in range(cols):

            y1 = int(
                row_index * cell_height
            )

            y2 = int(
                (row_index + 1)
                * cell_height
            )

            x1 = int(
                col_index * cell_width
            )

            x2 = int(
                (col_index + 1)
                * cell_width
            )

            cell_id = (
                f"{chr(65 + row_index)}"
                f"{col_index + 1}"
            )

            cell_image = image[
                y1:y2,
                x1:x2,
            ]

            cells.append(
                (
                    cell_id,
                    row_index + 1,
                    col_index + 1,
                    cell_image,
                )
            )

    return cells


# ============================================================
# Cell analysis
# ============================================================

def analyze_cell(
    cell_id: str,
    row: int,
    col: int,
    cell_image: np.ndarray,
) -> dict[str, Any]:

    exg = calculate_exg(
        cell_image
    )

    exg_min = float(
        np.min(exg)
    )

    exg_max = float(
        np.max(exg)
    )

    exg_average = float(
        np.mean(exg)
    )

    status, severity = (
        classify_exg(
            exg_average
        )
    )

    issue, recommendation = (
        recommendation_for_status(
            status,
            severity,
        )
    )

    confidence = (
        calculate_classification_confidence(
            exg_average,
            status,
        )
    )

    return {
        "id": cell_id,
        "row": row,
        "col": col,
        "status": status,
        "severity": severity,
        "confidence": confidence,
        "exg_value": round(
            exg_average,
            4,
        ),
        "exg_min": round(
            exg_min,
            4,
        ),
        "exg_max": round(
            exg_max,
            4,
        ),
        "issue": issue,
        "recommended_action": recommendation,
    }


def calculate_classification_confidence(
    exg_average: float,
    status: str,
) -> float:

    """
    Estimate confidence for the heuristic classification.

    This is NOT YOLO confidence.

    The value is based on distance from the
    nearest classification threshold.
    """

    if status == "healthy":

        distance = (
            exg_average
            - EXG_HEALTHY_THRESHOLD
        )

    elif status == "dry":

        distance = min(
            abs(
                exg_average
                - EXG_DRY_THRESHOLD
            ),
            abs(
                exg_average
                - EXG_HEALTHY_THRESHOLD
            ),
        )

    else:

        distance = min(
            abs(
                exg_average
                - EXG_CRITICAL_THRESHOLD
            ),
            abs(
                exg_average
                - EXG_DRY_THRESHOLD
            ),
        )

    confidence = 0.50 + (
        min(
            float(distance) / 60.0,
            1.0,
        )
        * 0.45
    )

    return round(
        max(
            0.50,
            min(
                confidence,
                0.95,
            ),
        ),
        3,
    )


# ============================================================
# Alerts
# ============================================================

def build_alerts(
    cells: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    alerts = []

    for cell in cells:

        if cell["status"] == "healthy":
            continue

        if cell["severity"] == "urgent":

            alerts.append(
                {
                    "cell": cell["id"],
                    "severity": "urgent",
                    "message": cell["issue"],
                    "action": cell[
                        "recommended_action"
                    ],
                }
            )

        else:

            alerts.append(
                {
                    "cell": cell["id"],
                    "severity": "warning",
                    "message": cell["issue"],
                    "action": cell[
                        "recommended_action"
                    ],
                }
            )

    return alerts


# ============================================================
# Overall health
# ============================================================

def calculate_overall_health(
    cells: list[dict[str, Any]],
) -> float:

    if not cells:
        return 0.0

    values = []

    for cell in cells:

        exg = float(
            cell["exg_value"]
        )

        normalized = (
            (
                exg
                - EXG_CRITICAL_THRESHOLD
            )
            / (
                EXG_HEALTHY_THRESHOLD
                - EXG_CRITICAL_THRESHOLD
            )
        )

        normalized = max(
            0.0,
            min(
                1.0,
                normalized,
            ),
        )

        values.append(
            normalized * 100.0
        )

    return round(
        float(
            np.mean(values)
        ),
        2,
    )


def overall_status_from_health(
    health: float,
) -> tuple[str, str]:

    if health >= 75:

        return (
            "healthy",
            "low",
        )

    if health >= 50:

        return (
            "dry",
            "medium",
        )

    if health >= 25:

        return (
            "dry",
            "high",
        )

    return (
        "critical",
        "urgent",
    )


def overall_recommendation(
    status: str,
    severity: str,
    cells: list[dict[str, Any]],
) -> tuple[str, str]:

    unhealthy = [
        cell
        for cell in cells
        if cell["status"] != "healthy"
    ]

    if status == "healthy":

        return (
            "No significant field-wide vegetation stress detected.",
            "Continue routine monitoring and inspect the field again during the next flight.",
        )

    if status == "dry":

        if unhealthy:

            affected = ", ".join(
                cell["id"]
                for cell in unhealthy[:6]
            )

            return (
                f"Vegetation stress detected in {len(unhealthy)} plot(s).",
                f"Inspect irrigation and soil moisture, especially around plots {affected}.",
            )

        return (
            "Possible field-wide moisture stress detected.",
            "Inspect irrigation coverage and soil moisture.",
        )

    return (
        "Severe vegetation stress detected in the field.",
        "Prioritize manual inspection of affected plots and investigate water stress, crop damage, or other causes immediately.",
    )


# ============================================================
# Database persistence
# ============================================================

def save_analysis_to_database(
    db: Session,
    farm_id: str,
    image_filename: str | None,
    timestamp: datetime,
    overall_health_pct: float,
    cells: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
    detections: list[dict[str, Any]],
) -> Analysis:

    """
    Persist the completed analysis and all of its
    child records.

    The Analysis record is created first so that its
    generated primary key can be used by cells,
    alerts, detections, and feedback relationships.
    """

    analysis = Analysis(
        farm_id=farm_id,
        timestamp=timestamp,
        overall_health_pct=overall_health_pct,
        image_filename=image_filename,
    )

    db.add(analysis)
    db.flush()

    # --------------------------------------------------------
    # Cells
    # --------------------------------------------------------

    for cell in cells:

        analysis_cell = AnalysisCell(
            analysis_id=analysis.id,
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

        db.add(analysis_cell)

    # --------------------------------------------------------
    # Alerts
    # --------------------------------------------------------

    for alert in alerts:

        analysis_alert = AnalysisAlert(
            analysis_id=analysis.id,
            cell=alert["cell"],
            severity=alert["severity"],
            message=alert["message"],
            action=alert.get(
                "action",
                "",
            ),
        )

        db.add(analysis_alert)

    # --------------------------------------------------------
    # YOLO detections
    # --------------------------------------------------------

    for detection in detections:

        bbox = detection.get(
            "bbox",
            [],
        )

        if len(bbox) < 4:
            continue

        analysis_detection = AnalysisDetection(
            analysis_id=analysis.id,
            class_id=int(
                detection.get(
                    "class_id",
                    0,
                )
            ),
            class_name=str(
                detection.get(
                    "class",
                    "unknown",
                )
            ),
            confidence=float(
                detection.get(
                    "confidence",
                    0.0,
                )
            ),
            bbox_x1=float(bbox[0]),
            bbox_y1=float(bbox[1]),
            bbox_x2=float(bbox[2]),
            bbox_y2=float(bbox[3]),
        )

        db.add(analysis_detection)

    db.commit()

    db.refresh(analysis)

    return analysis


# ============================================================
# Main service
# ============================================================

def analyze_crop(
    image_path: str | Path,
    image_filename: str | None = None,
    db: Session | None = None,
    farm_id: str = "AT1-DEMO",
    timestamp: str | None = None,
    cell_size_m: float = DEFAULT_CELL_SIZE_M,
) -> dict[str, Any]:

    """
    Main crop-analysis entry point.

    Supports both:

    1. Normal analysis
       analyze_crop(image_path=...)

    2. Upload/database analysis
       analyze_crop(
           image_path=...,
           image_filename=...,
           db=...,
           farm_id=...,
       )

    When a database session is supplied, the completed
    analysis is persisted automatically.
    """

    image_path = Path(
        image_path
    )

    image = load_image(
        image_path
    )

    height, width = (
        image.shape[:2]
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    if timestamp:

        try:

            analysis_timestamp = (
                datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )
            )

        except ValueError:

            analysis_timestamp = (
                datetime.utcnow()
            )

    else:

        analysis_timestamp = (
            datetime.utcnow()
        )

    # --------------------------------------------------------
    # 1. Grid analysis
    # --------------------------------------------------------

    raw_cells = split_into_cells(
        image,
        rows=ROWS,
        cols=COLS,
    )

    cells = []

    for (
        cell_id,
        row,
        col,
        cell_image,
    ) in raw_cells:

        cells.append(
            analyze_cell(
                cell_id,
                row,
                col,
                cell_image,
            )
        )

    # --------------------------------------------------------
    # 2. Overall ExG health
    # --------------------------------------------------------

    health = calculate_overall_health(
        cells
    )

    (
        overall_status,
        overall_severity,
    ) = overall_status_from_health(
        health
    )

    (
        overall_issue,
        overall_action,
    ) = overall_recommendation(
        overall_status,
        overall_severity,
        cells,
    )

    # --------------------------------------------------------
    # 3. Alerts
    # --------------------------------------------------------

    alerts = build_alerts(
        cells
    )

    # --------------------------------------------------------
    # 4. YOLO
    # --------------------------------------------------------

    try:

        detections = detect_objects(
            image_path
        )

        detector_info = (
            get_detector_info()
        )

        yolo_error = None

    except Exception as error:

        detections = []

        detector_info = {
            "model": None,
            "model_type": "unavailable",
            "crop_disease_detection": False,
        }

        yolo_error = str(error)

    # --------------------------------------------------------
    # 5. Database persistence
    # --------------------------------------------------------

    analysis_id = None

    if db is not None:

        saved_analysis = (
            save_analysis_to_database(
                db=db,
                farm_id=farm_id,
                image_filename=image_filename,
                timestamp=analysis_timestamp,
                overall_health_pct=health,
                cells=cells,
                alerts=alerts,
                detections=detections,
            )
        )

        analysis_id = (
            saved_analysis.id
        )

    # --------------------------------------------------------
    # 6. Final response
    # --------------------------------------------------------

    response: dict[str, Any] = {

        "analysis_id": analysis_id,

        "farm_id": farm_id,

        "timestamp": (
            analysis_timestamp.isoformat()
        ),

        "image": {
            "width": width,
            "height": height,
            "channels": int(
                image.shape[2]
            )
            if image.ndim == 3
            else 1,
        },

        "overall_health_pct": health,

        "overall_status": overall_status,

        "overall_severity": overall_severity,

        "overall_issue": overall_issue,

        "overall_recommended_action":
            overall_action,

        "grid": {
            "rows": ROWS,
            "cols": COLS,
            "cell_size_m": cell_size_m,
        },

        "cells": cells,

        "alerts": alerts,

        "detections": detections,

        "ai": {
            "vegetation_analysis": {
                "method": "ExG heuristic",
                "responsibility": (
                    "Primary crop vegetation-health signal"
                ),
            },

            "object_detection": {
                "method": "YOLO",
                "model": detector_info[
                    "model"
                ],
                "model_type": detector_info[
                    "model_type"
                ],
                "crop_disease_detection":
                    detector_info[
                        "crop_disease_detection"
                    ],
                "responsibility": (
                    "Additional visual object detection"
                ),
            },

            "yolo_error": yolo_error,
        },
    }

    return response

