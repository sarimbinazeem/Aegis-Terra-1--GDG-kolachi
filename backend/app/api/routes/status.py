from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/status",
    tags=["System"],
)
def status():
    """
    Confirm that the API is running.
    """

    return {
        "status": "online",
        "service": "Aegis-Terra API",
        "version": "1.0.0",
    }