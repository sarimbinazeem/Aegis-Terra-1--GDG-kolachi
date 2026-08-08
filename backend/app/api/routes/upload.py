from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.database.models import Farm

from app.schemas.analysis import (
    CropAnalysisResponse,
)

from app.services.upload_service import (
    save_uploaded_file,
)

from app.services.crop_analysis_service import (
    analyze_crop,
)


router = APIRouter()

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}

DEFAULT_FARM_ID = "AT1-DEMO"


@router.post(
    "/upload",
    response_model=CropAnalysisResponse,
    tags=["Upload"],
)
def upload_image(
    image: UploadFile = File(...),
    farm_id: str = Query(
        default=DEFAULT_FARM_ID
    ),
    db: Session = Depends(get_db),
):
    """
    Upload an image, analyze it,
    and save the analysis to the selected farm.
    """

    filename = image.filename or ""

    extension = (
        "."
        + filename.split(".")[-1].lower()
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG and PNG "
                "images are allowed."
            ),
        )

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type.",
        )

    # Make sure the farm exists.
    farm = (
        db.query(Farm)
        .filter(
            Farm.farm_id == farm_id
        )
        .first()
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail=f"Farm '{farm_id}' not found.",
        )

    try:
        saved_filename, file_path = (
            save_uploaded_file(image)
        )

        return analyze_crop(
            image_path=file_path,
            image_filename=saved_filename,
            db=db,
            farm_id=farm_id,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
        status_code=500,
        detail=f"Image analysis failed: {str(e)}",
        ) from e