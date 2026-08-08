
"""
Database models for Aegis-Terra.
"""

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Farm(Base):
    """
    Farmer's farm profile.
    """

    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    farm_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        default="AT1-DEMO Farm",
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    crop: Mapped[str] = mapped_column(
        String(100),
        default="Unknown",
    )

    language: Mapped[str] = mapped_column(
        String(50),
        default="English",
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )

    analyses = relationship(
        "Analysis",
        back_populates="farm",
    )


class Analysis(Base):
    """
    One completed crop analysis.
    """

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    farm_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("farms.farm_id"),
        default="AT1-DEMO",
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )

    overall_health_pct: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    image_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    farm = relationship(
        "Farm",
        back_populates="analyses",
    )

    cells = relationship(
        "AnalysisCell",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    alerts = relationship(
        "AnalysisAlert",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    detections = relationship(
        "AnalysisDetection",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    feedback = relationship(
        "AnalysisFeedback",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class AnalysisCell(Base):
    """
    Individual grid cell belonging to an analysis.
    """

    __tablename__ = "analysis_cells"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id"),
        index=True,
    )

    cell_id: Mapped[str] = mapped_column(
        String(20)
    )

    row: Mapped[int] = mapped_column(
        Integer
    )

    col: Mapped[int] = mapped_column(
        Integer
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    severity: Mapped[str] = mapped_column(
        String(50)
    )

    confidence: Mapped[float] = mapped_column(
        Float
    )

    exg_value: Mapped[float] = mapped_column(
        Float
    )

    issue: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    recommended_action: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    analysis = relationship(
        "Analysis",
        back_populates="cells",
    )


class AnalysisAlert(Base):
    """
    Alert generated from an analysis.
    """

    __tablename__ = "analysis_alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id"),
        index=True,
    )

    cell: Mapped[str] = mapped_column(
        String(20)
    )

    severity: Mapped[str] = mapped_column(
        String(50)
    )

    message: Mapped[str] = mapped_column(
        Text
    )

    action: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    analysis = relationship(
        "Analysis",
        back_populates="alerts",
    )


class AnalysisDetection(Base):
    """
    YOLO detection belonging to an analysis.
    """

    __tablename__ = "analysis_detections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id"),
        index=True,
    )

    class_id: Mapped[int] = mapped_column(
        Integer
    )

    class_name: Mapped[str] = mapped_column(
        String(100)
    )

    confidence: Mapped[float] = mapped_column(
        Float
    )

    bbox_x1: Mapped[float] = mapped_column(
        Float
    )

    bbox_y1: Mapped[float] = mapped_column(
        Float
    )

    bbox_x2: Mapped[float] = mapped_column(
        Float
    )

    bbox_y2: Mapped[float] = mapped_column(
        Float
    )

    analysis = relationship(
        "Analysis",
        back_populates="detections",
    )


class AnalysisFeedback(Base):
    """
    Farmer feedback for an analysis.
    """

    __tablename__ = "analysis_feedback"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id"),
        index=True,
    )

    rating: Mapped[int] = mapped_column(
        Integer,
    )

    comment: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )

    analysis = relationship(
        "Analysis",
        back_populates="feedback",
    )
