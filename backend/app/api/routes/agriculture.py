from fastapi import APIRouter, HTTPException

from app.agriculture.service import (
    get_crop,
    get_soil,
    list_crops,
    list_soils,
)


router = APIRouter(
    prefix="/agriculture",
    tags=["Agricultural Knowledge Base"],
)


@router.get("/crops")
def crops():
    return {
        "count": len(list_crops()),
        "crops": list_crops(),
    }


@router.get("/crops/{crop_name}")
def crop_details(crop_name: str):
    crop = get_crop(crop_name)

    if crop is None:
        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' not found.",
        )

    return crop


@router.get("/soils")
def soils():
    return {
        "count": len(list_soils()),
        "soils": list_soils(),
    }


@router.get("/soils/{soil_name}")
def soil_details(soil_name: str):
    soil = get_soil(soil_name)

    if soil is None:
        raise HTTPException(
            status_code=404,
            detail=f"Soil '{soil_name}' not found.",
        )

    return soil