"""
Farm profile persistence service.
"""

from sqlalchemy.orm import Session

from app.database.models import Farm


DEFAULT_FARM_ID = "AT1-DEMO"


def get_farm(
    db: Session,
    farm_id: str,
) -> Farm | None:
    """
    Get one farm by farm_id.
    """

    return (
        db.query(Farm)
        .filter(
            Farm.farm_id == farm_id
        )
        .first()
    )


def get_farms(
    db: Session,
):
    """
    Get all farms.
    """

    return (
        db.query(Farm)
        .order_by(
            Farm.created_at.desc()
        )
        .all()
    )


def create_farm(
    db: Session,
    farm_id: str,
    name: str,
    latitude: float | None,
    longitude: float | None,
    crop: str,
    language: str,
) -> Farm:

    existing = get_farm(
        db,
        farm_id,
    )

    if existing:
        raise ValueError(
            f"Farm '{farm_id}' already exists."
        )

    farm = Farm(
        farm_id=farm_id,
        name=name,
        latitude=latitude,
        longitude=longitude,
        crop=crop,
        language=language,
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm


def update_farm(
    db: Session,
    farm: Farm,
    name: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    crop: str | None = None,
    language: str | None = None,
) -> Farm:

    if name is not None:
        farm.name = name

    if latitude is not None:
        farm.latitude = latitude

    if longitude is not None:
        farm.longitude = longitude

    if crop is not None:
        farm.crop = crop

    if language is not None:
        farm.language = language

    db.commit()
    db.refresh(farm)

    return farm