import os

from fastapi import APIRouter, HTTPException

from app.services.image_service import (
    load_image,
    get_image_info,
)

from app.services.grid_service import (
    split_into_grid,
    analyze_grid,
)

from app.services.ai_service import analyze_image
from app.services.alert_service import generate_alerts
from app.services.response_service import build_response


router = APIRouter()


@router.get(
    "/image-info/{filename}",
    tags=["Image"],
)
async def image_info(
    filename: str,
):
    """
    Analyze an already-uploaded image.

    This endpoint is primarily useful for debugging
    and inspecting an image directly.
    """

    image_path = os.path.join(
        "app",
        "uploads",
        filename,
    )

    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail="Image not found.",
        )

    try:
        # Load image
        image = load_image(image_path)

        # Grid analysis
        cells = split_into_grid(image)

        grid_results = analyze_grid(cells)

        # YOLO
        detections = analyze_image(
            image_path
        )

        # Alerts
        alerts = generate_alerts(
            grid_results
        )

        # Final response
        return build_response(
            grid_results,
            detections,
            alerts,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(e)}",
        )