
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parents[2]

CACHE_DIR = BASE_DIR / "data" / "weather_cache"


def _cache_path(farm_id: str) -> Path:
    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_id = "".join(
        character
        for character in farm_id
        if character.isalnum()
        or character in ("-", "_")
    )

    return CACHE_DIR / f"{safe_id}.json"


def save_weather_cache(
    farm_id: str,
    data: dict,
) -> None:

    path = _cache_path(farm_id)

    payload = {
        "cached_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "data": data,
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )


def load_weather_cache(
    farm_id: str,
) -> Optional[dict]:

    path = _cache_path(farm_id)

    if not path.exists():
        return None

    try:

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return payload.get("data")

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return None
