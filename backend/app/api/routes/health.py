from fastapi import APIRouter

from app.schemas.health import HealthResponse


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
def health_check():

    return {
        "status": "healthy",
        "service": "Aegis-Terra 1 Backend",
        "version": "1.0.0",
    }