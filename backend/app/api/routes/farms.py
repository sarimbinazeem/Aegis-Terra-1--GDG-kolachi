"""
Farm profile API routes.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)

from app.schemas.farm import (
    FarmCreate,
    FarmUpdate,
    FarmResponse,
)

from app.services.farm_service import (
    get_farm,
    get_farms,
    create_farm,
    update_farm,
)


router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
)


@router.get(
    "",
    response_model=list[FarmResponse],
)
def list_farms(
    db: Session = Depends(get_db),
):
    """
    Return all farm profiles.
    """

    return get_farms(db)


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
)
def get_one_farm(
    farm_id: str,
    db: Session = Depends(get_db),
):
    """
    Return one farm profile.
    """

    farm = get_farm(
        db,
        farm_id,
    )

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )

    return farm


@router.post(
    "",
    response_model=FarmResponse,
)
def create_new_farm(
    farm: FarmCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new farm profile.
    """

    try:

        return create_farm(
            db=db,
            farm_id=farm.farm_id,
            name=farm.name,
            latitude=farm.latitude,
            longitude=farm.longitude,
            crop=farm.crop,
            language=farm.language,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=409,
            detail=str(e),
        )


@router.put(
    "/{farm_id}",
    response_model=FarmResponse,
)
def update_existing_farm(
    farm_id: str,
    farm_data: FarmUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing farm profile.
    """

    farm = get_farm(
        db,
        farm_id,
    )

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )

    return update_farm(
        db=db,
        farm=farm,
        name=farm_data.name,
        latitude=farm_data.latitude,
        longitude=farm_data.longitude,
        crop=farm_data.crop,
        language=farm_data.language,
    )