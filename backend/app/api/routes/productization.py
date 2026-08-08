"""
Phase 10 productization endpoints.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.database.models import (
    Analysis,
    AnalysisFeedback,
)

from app.services.productization_service import (
    build_productization_summary,
)


router = APIRouter()


@router.get(
    "/analysis/{analysis_id}/insights",
    tags=["Productization"],
)
def analysis_insights(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    """
    Return product-level insights for an analysis.
    """

    current = (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id
        )
        .first()
    )

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    previous = (
        db.query(Analysis)
        .filter(
            Analysis.farm_id
            == current.farm_id,
            Analysis.id
            != current.id,
            Analysis.timestamp
            < current.timestamp,
        )
        .order_by(
            Analysis.timestamp.desc()
        )
        .first()
    )

    return build_productization_summary(
        current,
        previous,
    )


class FeedbackRequest(BaseModel):
    rating: int
    comment: str = ""


@router.post(
    "/analysis/{analysis_id}/feedback",
    tags=["Productization"],
)
def submit_feedback(
    analysis_id: int,
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
):
    """
    Store farmer feedback.
    """

    analysis = (
        db.query(Analysis)
        .filter(
            Analysis.id == analysis_id
        )
        .first()
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found.",
        )

    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5.",
        )

    record = AnalysisFeedback(
        analysis_id=analysis_id,
        rating=feedback.rating,
        comment=feedback.comment,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Feedback saved.",
        "id": record.id,
        "analysis_id": analysis_id,
    }