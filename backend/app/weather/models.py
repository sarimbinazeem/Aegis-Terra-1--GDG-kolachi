
from typing import Optional

from pydantic import BaseModel


class CurrentWeather(BaseModel):
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    precipitation_mm: Optional[float] = None
    rain_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    weather_code: Optional[int] = None
    is_day: Optional[bool] = None


class DailyWeather(BaseModel):
    date: str
    temperature_max_c: Optional[float] = None
    temperature_min_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    rain_mm: Optional[float] = None
    precipitation_probability_pct: Optional[float] = None


class WeatherData(BaseModel):
    farm_id: str
    latitude: float
    longitude: float

    source: str
    cached: bool
    fetched_at: str

    current: CurrentWeather
    forecast: list[DailyWeather]

    recent_rainfall_mm: Optional[float] = None
