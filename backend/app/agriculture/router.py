"""
Aegis-Terra Agricultural Knowledge Base API.

Phase 3 endpoints:
    GET /agriculture/status
    GET /agriculture/crops
    GET /agriculture/crops/{crop_name}
    GET /agriculture/crops/{crop_name}/stages
    GET /agriculture/crops/{crop_name}/stresses
    GET /agriculture/context/{crop_name}
"""

from fastapi import APIRouter, HTTPException, Query

from .knowledge_base import (
    get_agricultural_context,
    get_crop,
    get_growth_stages,
    get_stress_conditions,
    knowledge_base_status,
    list_crops,
)


router = APIRouter(
    prefix="/agriculture",
    tags=["Agricultural Knowledge Base"],
)


# ============================================================
# STATUS
# ============================================================

@router.get("/status")
def agriculture_status():
    """
    Verify that the local agricultural knowledge base
    is available.
    """

    return knowledge_base_status()


# ============================================================
# LIST CROPS
# ============================================================

@router.get("/crops")
def agriculture_crops():
    """
    Return all crops available in the local knowledge base.
    """

    return {
        "count": len(list_crops()),
        "crops": list_crops(),
    }


# ============================================================
# GET CROP
# ============================================================

@router.get("/crops/{crop_name}")
def agriculture_crop(
    crop_name: str,
):
    """
    Return complete agricultural information for a crop.
    """

    crop = get_crop(crop_name)

    if crop is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Crop '{crop_name}' was not found "
                "in the local agricultural knowledge base."
            ),
        )

    return crop


# ============================================================
# GROWTH STAGES
# ============================================================

@router.get("/crops/{crop_name}/stages")
def agriculture_crop_stages(
    crop_name: str,
):
    """
    Return growth stages for a crop.
    """

    crop = get_crop(crop_name)

    if crop is None:

        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' was not found.",
        )

    return {
        "crop": crop["name"],
        "growth_stages": get_growth_stages(crop_name),
    }


# ============================================================
# STRESS CONDITIONS
# ============================================================

@router.get("/crops/{crop_name}/stresses")
def agriculture_crop_stresses(
    crop_name: str,
):
    """
    Return known stress conditions for a crop.
    """

    crop = get_crop(crop_name)

    if crop is None:

        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' was not found.",
        )

    return {
        "crop": crop["name"],
        "stress_conditions":
            get_stress_conditions(crop_name),
    }


# ============================================================
# STRUCTURED CONTEXT
# ============================================================

@router.get("/context/{crop_name}")
def agriculture_context(
    crop_name: str,

    growth_stage: str | None = Query(
        default=None,
        description=(
            "Optional growth stage, for example "
            "vegetative or flowering."
        ),
    ),
):
    """
    Return the structured crop context that Phase 6 will use.
    """

    context = get_agricultural_context(
        crop_name,
        growth_stage,
    )

    if context is None:

        raise HTTPException(
            status_code=404,
            detail=f"Crop '{crop_name}' was not found.",
        )

    return context