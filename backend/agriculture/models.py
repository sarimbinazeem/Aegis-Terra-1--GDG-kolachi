from typing import Optional

from pydantic import BaseModel


class CropSummary(BaseModel):
    id: int
    name: str
    scientific_name: Optional[str] = None
    description: Optional[str] = None


class CropDetails(BaseModel):
    id: int
    name: str
    scientific_name: Optional[str] = None
    description: Optional[str] = None

    min_temperature_c: Optional[float] = None
    max_temperature_c: Optional[float] = None

    min_rainfall_mm: Optional[float] = None
    max_rainfall_mm: Optional[float] = None

    min_ph: Optional[float] = None
    max_ph: Optional[float] = None

    water_requirement: Optional[str] = None
    preferred_soil_texture: Optional[str] = None
    water_retention: Optional[str] = None
    drainage: Optional[str] = None


class GrowthStage(BaseModel):
    id: int
    crop_id: int
    stage_name: str
    duration_days: Optional[int] = None
    min_temperature_c: Optional[float] = None
    max_temperature_c: Optional[float] = None
    water_requirement: Optional[str] = None
    notes: Optional[str] = None


class StressCondition(BaseModel):
    id: int
    crop_id: int
    condition_name: str
    indicators: Optional[str] = None
    severity: Optional[str] = None
    recommendation: Optional[str] = None


class SoilProfile(BaseModel):
    id: int
    name: str
    texture: str
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    water_retention: Optional[str] = None
    drainage: Optional[str] = None
    description: Optional[str] = None