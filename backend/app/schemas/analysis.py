
from pydantic import BaseModel, Field


class Detection(BaseModel):
    class_id: int
    class_name: str = Field(alias="class")
    confidence: float
    bbox: list[float]


class Cell(BaseModel):
    id: str
    row: int
    col: int

    status: str
    severity: str
    confidence: float

    issue: str
    recommended_action: str

    exg_value: float


class Grid(BaseModel):
    rows: int
    cols: int
    cell_size_m: int


class Alert(BaseModel):
    cell: str
    severity: str
    message: str
    action: str


class CropAnalysisResponse(BaseModel):
    analysis_id: int | None = None

    farm_id: str
    timestamp: str | None

    overall_health_pct: float | None

    overall_status: str | None = None
    overall_severity: str | None = None
    overall_issue: str | None = None
    overall_recommended_action: str | None = None

    grid: Grid
    cells: list[Cell]
    detections: list[Detection]
    alerts: list[Alert]
