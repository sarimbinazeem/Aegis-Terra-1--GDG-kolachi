
from datetime import datetime, timezone

from .cache import (
    load_weather_cache,
    save_weather_cache,
)

from .client import fetch_weather


def _build_weather_data(
    farm_id: str,
    latitude: float,
    longitude: float,
    raw: dict,
) -> dict:

    current = raw.get(
        "current",
        {},
    )

    daily = raw.get(
        "daily",
        {},
    )

    dates = daily.get(
        "time",
        [],
    )

    max_temps = daily.get(
        "temperature_2m_max",
        [],
    )

    min_temps = daily.get(
        "temperature_2m_min",
        [],
    )

    precipitation = daily.get(
        "precipitation_sum",
        [],
    )

    rain = daily.get(
        "rain_sum",
        [],
    )

    precipitation_probability = daily.get(
        "precipitation_probability_max",
        [],
    )

    forecast = []

    for index, date in enumerate(dates):

        forecast.append(
            {
                "date": date,

                "temperature_max_c": (
                    max_temps[index]
                    if index < len(max_temps)
                    else None
                ),

                "temperature_min_c": (
                    min_temps[index]
                    if index < len(min_temps)
                    else None
                ),

                "precipitation_mm": (
                    precipitation[index]
                    if index < len(precipitation)
                    else None
                ),

                "rain_mm": (
                    rain[index]
                    if index < len(rain)
                    else None
                ),

                "precipitation_probability_pct": (
                    precipitation_probability[index]
                    if index < len(
                        precipitation_probability
                    )
                    else None
                ),
            }
        )

    # The first three daily records represent
    # the recent-past window requested from
    # Open-Meteo.
    recent_rainfall = sum(
        item["rain_mm"] or 0
        for item in forecast[:3]
    )

    return {
        "farm_id": farm_id,

        "latitude": latitude,
        "longitude": longitude,

        "source": "Open-Meteo",

        "cached": False,

        "fetched_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "current": {
            "temperature_c": current.get(
                "temperature_2m"
            ),

            "humidity_pct": current.get(
                "relative_humidity_2m"
            ),

            "precipitation_mm": current.get(
                "precipitation"
            ),

            "rain_mm": current.get(
                "rain"
            ),

            "wind_speed_kmh": current.get(
                "wind_speed_10m"
            ),

            "weather_code": current.get(
                "weather_code"
            ),

            "is_day": (
                bool(current["is_day"])
                if current.get("is_day")
                is not None
                else None
            ),
        },

        "forecast": forecast,

        "recent_rainfall_mm": round(
            recent_rainfall,
            2,
        ),
    }


def get_weather(
    farm_id: str,
    latitude: float,
    longitude: float,
) -> dict:

    try:

        raw = fetch_weather(
            latitude,
            longitude,
        )

        weather = _build_weather_data(
            farm_id,
            latitude,
            longitude,
            raw,
        )

        save_weather_cache(
            farm_id,
            weather,
        )

        return weather

    except Exception as error:

        cached = load_weather_cache(
            farm_id
        )

        if cached is None:

            raise RuntimeError(
                "Weather service unavailable "
                "and no cached weather exists."
            ) from error

        cached["cached"] = True

        return cached
