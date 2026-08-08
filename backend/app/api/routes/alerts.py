from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Analysis
from app.database.models import AnalysisAlert


router = APIRouter()


@router.get(
    "/alerts",
    tags=["Alerts"],
)
def get_alerts(
    db: Session = Depends(get_db),
):
    """
    Return alerts from the latest farm analysis.
    """

    analysis = (
        db.query(Analysis)
        .order_by(
            Analysis.timestamp.desc()
        )
        .first()
    )

    if analysis is None:
        return []

    return [
        {
            "id": alert.id,
            "analysis_id": analysis.id,
            "cell": alert.cell,
            "severity": alert.severity,
            "message": alert.message,
            "action": alert.action,
        }
        for alert in analysis.alerts
    ]