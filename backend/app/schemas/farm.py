"""
Schemas for farm profile APIs.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class FarmCreate(BaseModel):
    farm_id: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    latitude: float | None = None

    longitude: float | None = None

    crop: str = Field(
        default="Unknown",
        max_length=100,
    )

    language: str = Field(
        default="English",
        max_length=50,
    )


class FarmUpdate(BaseModel):
    name: str | None = None

    latitude: float | None = None

    longitude: float | None = None

    crop: str | None = None

    language: str | None = None


class FarmResponse(BaseModel):
    id: int
    farm_id: str
    name: str
    latitude: float | None
    longitude: float | None
    crop: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True
