from fastapi import APIRouter, HTTPException

from app.weather.service import get_weather


router = APIRouter(
    prefix="/weather",
    tags=["Weather Intelligence"],
)


@router.get("/farm/{farm_id}")
def farm_weather(
    farm_id: str,
    latitude: float,
    longitude: float,
):

    try:

        return get_weather(
            farm_id=farm_id,
            latitude=latitude,
            longitude=longitude,
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )