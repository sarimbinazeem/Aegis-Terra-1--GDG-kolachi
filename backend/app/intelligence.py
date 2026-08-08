"""
Aegis-Terra Intelligence Layer

Phases 3-10:
- Local agricultural knowledge base
- Weather context
- Soil context
- Context + recommendation engine
- LLM integration
- Farmer-friendly output
- Offline caching/fallbacks
- Scan history and alerts

This module is deliberately additive. It does not replace the
existing image analysis/upload pipeline.

Phase 7:
Groq LLM integration receives ONLY structured, validated
agricultural context. It does not diagnose crops directly
from images.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ============================================================
# Environment
# ============================================================

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = (
    Path(__file__).resolve().parents[1]
    if len(Path(__file__).resolve().parents) >= 2
    else Path.cwd()
)

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(
    os.getenv(
        "AEGIS_DB_PATH",
        str(DATA_DIR / "aegis_terra.db"),
    )
)

# ============================================================
# Groq configuration
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)

GROQ_API_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_TIMEOUT_SECONDS = 20

# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/intelligence",
    tags=["Aegis-Terra Intelligence"],
)

# ============================================================
# Database
# ============================================================


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS farms (
                farm_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                crop TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'English',
                latitude REAL,
                longitude REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                aliases TEXT NOT NULL DEFAULT '[]',
                growth_stages TEXT NOT NULL DEFAULT '[]',
                min_temp_c REAL,
                max_temp_c REAL,
                ideal_temp_c REAL,
                water_need_mm_week REAL,
                soil_types TEXT NOT NULL DEFAULT '[]',
                ph_min REAL,
                ph_max REAL,
                stress_conditions TEXT NOT NULL DEFAULT '[]',
                recommendations TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS soil_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                texture TEXT NOT NULL,
                ph REAL,
                sand_pct REAL,
                clay_pct REAL,
                water_retention TEXT NOT NULL,
                drainage TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'local-demo-dataset',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS environmental_cache (
                cache_key TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                payload TEXT NOT NULL,
                fetched_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id TEXT NOT NULL,
                scan_time TEXT NOT NULL,
                overall_health_pct REAL NOT NULL,
                overall_status TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                recommendation_json TEXT,
                FOREIGN KEY(farm_id) REFERENCES farms(farm_id)
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farm_id TEXT NOT NULL,
                scan_id INTEGER,
                zone_id TEXT,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                acknowledged INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(farm_id) REFERENCES farms(farm_id),
                FOREIGN KEY(scan_id) REFERENCES scans(id)
            );
            """
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# Phase 3 — Local Agricultural Knowledge Base
# ============================================================

CROP_SEED = [
    {
        "name": "Wheat",
        "aliases": ["gandum"],
        "growth_stages": [
            {"stage": "germination", "days": "0-10"},
            {"stage": "tillering", "days": "20-45"},
            {"stage": "stem_extension", "days": "45-80"},
            {"stage": "heading", "days": "80-110"},
            {"stage": "grain_filling", "days": "110-140"},
        ],
        "min_temp_c": 5,
        "max_temp_c": 30,
        "ideal_temp_c": 20,
        "water_need_mm_week": 25,
        "soil_types": ["loam", "sandy loam", "clay loam"],
        "ph_min": 6.0,
        "ph_max": 7.5,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "waterlogging",
            "nutrient stress",
        ],
        "recommendations": [
            "Check irrigation when rainfall is low and temperatures are high.",
            "Avoid prolonged waterlogging.",
            "Inspect stressed zones again after corrective irrigation.",
        ],
    },
    {
        "name": "Rice",
        "aliases": ["chawal"],
        "growth_stages": [
            {"stage": "germination", "days": "0-10"},
            {"stage": "vegetative", "days": "10-50"},
            {"stage": "panicle_initiation", "days": "50-75"},
            {"stage": "flowering", "days": "75-100"},
            {"stage": "grain_filling", "days": "100-130"},
        ],
        "min_temp_c": 18,
        "max_temp_c": 35,
        "ideal_temp_c": 28,
        "water_need_mm_week": 45,
        "soil_types": ["clay", "clay loam", "loam"],
        "ph_min": 5.5,
        "ph_max": 7.0,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "waterlogging",
            "pest pressure",
        ],
        "recommendations": [
            "Monitor water availability closely during flowering.",
            "Inspect for pest symptoms when stress is localized.",
            "Avoid abrupt drying during sensitive growth stages.",
        ],
    },
    {
        "name": "Maize",
        "aliases": ["corn", "makai"],
        "growth_stages": [
            {"stage": "germination", "days": "0-10"},
            {"stage": "vegetative", "days": "10-45"},
            {"stage": "tasseling", "days": "45-65"},
            {"stage": "silking", "days": "65-80"},
            {"stage": "grain_filling", "days": "80-120"},
        ],
        "min_temp_c": 10,
        "max_temp_c": 35,
        "ideal_temp_c": 25,
        "water_need_mm_week": 30,
        "soil_types": ["loam", "sandy loam", "clay loam"],
        "ph_min": 5.8,
        "ph_max": 7.2,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "nutrient stress",
            "pest pressure",
        ],
        "recommendations": [
            "Check irrigation during tasseling and silking.",
            "Look for uniformity of stress across neighboring grid cells.",
            "Inspect leaves for pest damage if stress is localized.",
        ],
    },
    {
        "name": "Cotton",
        "aliases": ["cotton"],
        "growth_stages": [
            {"stage": "emergence", "days": "0-15"},
            {"stage": "vegetative", "days": "15-45"},
            {"stage": "squaring", "days": "45-70"},
            {"stage": "flowering", "days": "70-110"},
            {"stage": "boll_development", "days": "110-160"},
        ],
        "min_temp_c": 15,
        "max_temp_c": 38,
        "ideal_temp_c": 28,
        "water_need_mm_week": 30,
        "soil_types": ["loam", "sandy loam", "clay loam"],
        "ph_min": 5.5,
        "ph_max": 8.0,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "pest pressure",
            "nutrient stress",
        ],
        "recommendations": [
            "Check irrigation during flowering and boll development.",
            "Inspect stressed zones for pest damage.",
            "Compare current scan with previous scans before escalating.",
        ],
    },
    {
        "name": "Sugarcane",
        "aliases": ["sugar cane", "ganna"],
        "growth_stages": [
            {"stage": "germination", "days": "0-30"},
            {"stage": "tillering", "days": "30-90"},
            {"stage": "grand_growth", "days": "90-210"},
            {"stage": "maturation", "days": "210-365"},
        ],
        "min_temp_c": 15,
        "max_temp_c": 38,
        "ideal_temp_c": 28,
        "water_need_mm_week": 35,
        "soil_types": ["loam", "clay loam", "sandy loam"],
        "ph_min": 6.0,
        "ph_max": 7.5,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "waterlogging",
            "pest pressure",
        ],
        "recommendations": [
            "Check water distribution and drainage.",
            "Prioritize persistent stressed zones for field inspection.",
        ],
    },
    {
        "name": "Tomato",
        "aliases": ["tamatar"],
        "growth_stages": [
            {"stage": "seedling", "days": "0-30"},
            {"stage": "vegetative", "days": "30-55"},
            {"stage": "flowering", "days": "55-75"},
            {"stage": "fruiting", "days": "75-120"},
        ],
        "min_temp_c": 12,
        "max_temp_c": 32,
        "ideal_temp_c": 24,
        "water_need_mm_week": 30,
        "soil_types": ["loam", "sandy loam"],
        "ph_min": 6.0,
        "ph_max": 6.8,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "pest pressure",
            "disease pressure",
        ],
        "recommendations": [
            "Keep irrigation consistent rather than alternating very dry and very wet conditions.",
            "Inspect localized stress for disease or pest symptoms.",
        ],
    },
    {
        "name": "Potato",
        "aliases": ["aloo"],
        "growth_stages": [
            {"stage": "sprouting", "days": "0-20"},
            {"stage": "vegetative", "days": "20-50"},
            {"stage": "tuber_formation", "days": "50-80"},
            {"stage": "tuber_bulking", "days": "80-110"},
        ],
        "min_temp_c": 7,
        "max_temp_c": 30,
        "ideal_temp_c": 20,
        "water_need_mm_week": 25,
        "soil_types": ["sandy loam", "loam"],
        "ph_min": 5.0,
        "ph_max": 6.5,
        "stress_conditions": [
            "water stress",
            "heat stress",
            "disease pressure",
        ],
        "recommendations": [
            "Avoid prolonged water stress during tuber formation.",
            "Inspect localized yellowing or decline for disease symptoms.",
        ],
    },
    {
        "name": "Chickpea",
        "aliases": ["chana"],
        "growth_stages": [
            {"stage": "germination", "days": "0-15"},
            {"stage": "vegetative", "days": "15-45"},
            {"stage": "flowering", "days": "45-75"},
            {"stage": "pod_filling", "days": "75-110"},
        ],
        "min_temp_c": 10,
        "max_temp_c": 30,
        "ideal_temp_c": 20,
        "water_need_mm_week": 18,
        "soil_types": ["loam", "sandy loam"],
        "ph_min": 6.0,
        "ph_max": 8.0,
        "stress_conditions": [
            "water stress",
            "waterlogging",
            "disease pressure",
        ],
        "recommendations": [
            "Avoid excessive irrigation and poor drainage.",
            "Monitor flowering and pod filling for water stress.",
        ],
    },
]

SOIL_SEED = [
    {
        "region_key": "default",
        "name": "General loam profile",
        "texture": "loam",
        "ph": 6.8,
        "sand_pct": 40,
        "clay_pct": 25,
        "water_retention": "medium",
        "drainage": "good",
    },
    {
        "region_key": "karachi",
        "name": "Karachi demo soil profile",
        "texture": "sandy loam",
        "ph": 7.7,
        "sand_pct": 68,
        "clay_pct": 12,
        "water_retention": "low",
        "drainage": "fast",
    },
    {
        "region_key": "lahore",
        "name": "Punjab loam demo profile",
        "texture": "loam",
        "ph": 7.2,
        "sand_pct": 42,
        "clay_pct": 24,
        "water_retention": "medium",
        "drainage": "good",
    },
    {
        "region_key": "multan",
        "name": "Multan sandy loam demo profile",
        "texture": "sandy loam",
        "ph": 7.8,
        "sand_pct": 65,
        "clay_pct": 14,
        "water_retention": "low",
        "drainage": "fast",
    },
]


def seed_knowledge_base() -> None:
    with connect_db() as db:
        for c in CROP_SEED:
            db.execute(
                """
                INSERT INTO crops
                (
                    name,
                    aliases,
                    growth_stages,
                    min_temp_c,
                    max_temp_c,
                    ideal_temp_c,
                    water_need_mm_week,
                    soil_types,
                    ph_min,
                    ph_max,
                    stress_conditions,
                    recommendations
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    aliases=excluded.aliases,
                    growth_stages=excluded.growth_stages,
                    min_temp_c=excluded.min_temp_c,
                    max_temp_c=excluded.max_temp_c,
                    ideal_temp_c=excluded.ideal_temp_c,
                    water_need_mm_week=excluded.water_need_mm_week,
                    soil_types=excluded.soil_types,
                    ph_min=excluded.ph_min,
                    ph_max=excluded.ph_max,
                    stress_conditions=excluded.stress_conditions,
                    recommendations=excluded.recommendations
                """,
                (
                    c["name"],
                    json.dumps(c["aliases"]),
                    json.dumps(c["growth_stages"]),
                    c["min_temp_c"],
                    c["max_temp_c"],
                    c["ideal_temp_c"],
                    c["water_need_mm_week"],
                    json.dumps(c["soil_types"]),
                    c["ph_min"],
                    c["ph_max"],
                    json.dumps(c["stress_conditions"]),
                    json.dumps(c["recommendations"]),
                ),
            )

        for s in SOIL_SEED:
            db.execute(
                """
                INSERT INTO soil_profiles
                (
                    region_key,
                    name,
                    texture,
                    ph,
                    sand_pct,
                    clay_pct,
                    water_retention,
                    drainage,
                    source,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(region_key) DO UPDATE SET
                    name=excluded.name,
                    texture=excluded.texture,
                    ph=excluded.ph,
                    sand_pct=excluded.sand_pct,
                    clay_pct=excluded.clay_pct,
                    water_retention=excluded.water_retention,
                    drainage=excluded.drainage,
                    source=excluded.source,
                    updated_at=excluded.updated_at
                """,
                (
                    s["region_key"],
                    s["name"],
                    s["texture"],
                    s["ph"],
                    s["sand_pct"],
                    s["clay_pct"],
                    s["water_retention"],
                    s["drainage"],
                    "local-demo-dataset",
                    now_iso(),
                ),
            )


def _decode_crop(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)

    for key in (
        "aliases",
        "growth_stages",
        "soil_types",
        "stress_conditions",
        "recommendations",
    ):
        data[key] = json.loads(data[key])

    return data


def get_crop(
    crop_name: str,
) -> Optional[dict[str, Any]]:
    with connect_db() as db:
        row = db.execute(
            """
            SELECT *
            FROM crops
            WHERE lower(name)=lower(?)
            OR lower(aliases) LIKE ?
            """,
            (
                crop_name,
                f'%"{crop_name.lower()}"%',
            ),
        ).fetchone()

    return _decode_crop(row) if row else None


# ============================================================
# Models
# ============================================================


class FarmUpsert(BaseModel):
    farm_id: str
    name: str
    crop: str
    language: str = "English"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ScanInput(BaseModel):
    farm_id: str
    overall_health_pct: float = Field(
        ge=0,
        le=100,
    )
    overall_status: str = "unknown"
    cells: list[dict[str, Any]] = Field(
        default_factory=list
    )
    source: str = "image-analysis"


class RecommendationInput(BaseModel):
    farm_id: str
    analysis: dict[str, Any]
    weather: Optional[dict[str, Any]] = None
    soil: Optional[dict[str, Any]] = None


class LLMExplainInput(BaseModel):
    farm_id: str
    analysis: dict[str, Any]
    recommendation: dict[str, Any]
    weather: Optional[dict[str, Any]] = None
    soil: Optional[dict[str, Any]] = None


# ============================================================
# Phase 4 — Weather
# ============================================================


def _cache_get(
    key: str,
) -> Optional[dict[str, Any]]:
    with connect_db() as db:
        row = db.execute(
            """
            SELECT payload, expires_at
            FROM environmental_cache
            WHERE cache_key=?
            """,
            (key,),
        ).fetchone()

    if not row:
        return None

    if (
        datetime.fromisoformat(row["expires_at"])
        < datetime.now(timezone.utc)
    ):
        return None

    return json.loads(row["payload"])


def _cache_put(
    key: str,
    kind: str,
    lat: float,
    lon: float,
    payload: dict[str, Any],
    ttl_hours: int,
) -> None:
    fetched = datetime.now(timezone.utc)
    expires = fetched + timedelta(
        hours=ttl_hours
    )

    with connect_db() as db:
        db.execute(
            """
            INSERT INTO environmental_cache
            (
                cache_key,
                kind,
                latitude,
                longitude,
                payload,
                fetched_at,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
                payload=excluded.payload,
                fetched_at=excluded.fetched_at,
                expires_at=excluded.expires_at
            """,
            (
                key,
                kind,
                lat,
                lon,
                json.dumps(payload),
                fetched.isoformat(),
                expires.isoformat(),
            ),
        )


def _stale_cache(
    key: str,
) -> Optional[dict[str, Any]]:
    with connect_db() as db:
        row = db.execute(
            """
            SELECT payload
            FROM environmental_cache
            WHERE cache_key=?
            """,
            (key,),
        ).fetchone()

    return (
        json.loads(row["payload"])
        if row
        else None
    )


def fetch_weather(
    lat: float,
    lon: float,
) -> dict[str, Any]:

    key = (
        f"weather:{round(lat, 2)}:"
        f"{round(lon, 2)}"
    )

    cached = _cache_get(key)

    if cached:
        cached["source"] = "cache"
        return cached

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urllib.parse.urlencode(
            {
                "latitude": lat,
                "longitude": lon,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "precipitation"
                ),
                "daily": (
                    "temperature_2m_max,"
                    "precipitation_sum"
                ),
                "forecast_days": 3,
                "timezone": "auto",
            }
        )
    )

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Aegis-Terra/1.0"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=8,
        ) as response:
            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        result = {
            "temperature_c": data.get(
                "current",
                {},
            ).get(
                "temperature_2m"
            ),
            "humidity_pct": data.get(
                "current",
                {},
            ).get(
                "relative_humidity_2m"
            ),
            "rainfall_mm": data.get(
                "current",
                {},
            ).get(
                "precipitation"
            ),
            "forecast": {
                "dates": data.get(
                    "daily",
                    {},
                ).get(
                    "time",
                    [],
                ),
                "max_temp_c": data.get(
                    "daily",
                    {},
                ).get(
                    "temperature_2m_max",
                    [],
                ),
                "rainfall_mm": data.get(
                    "daily",
                    {},
                ).get(
                    "precipitation_sum",
                    [],
                ),
            },
            "source": "open-meteo",
            "fetched_at": now_iso(),
        }

        _cache_put(
            key,
            "weather",
            lat,
            lon,
            result,
            ttl_hours=3,
        )

        return result

    except Exception as exc:
        stale = _stale_cache(key)

        if stale:
            stale["source"] = "stale-cache"
            stale["warning"] = (
                "Weather update unavailable: "
                f"{type(exc).__name__}"
            )
            return stale

        return {
            "temperature_c": None,
            "humidity_pct": None,
            "rainfall_mm": None,
            "forecast": {},
            "source": "unavailable",
            "warning": (
                "Weather unavailable: "
                f"{type(exc).__name__}"
            ),
        }


# ============================================================
# Phase 5 — Soil Intelligence
# ============================================================


def _region_from_coords(
    lat: Optional[float],
    lon: Optional[float],
) -> str:

    if lat is None or lon is None:
        return "default"

    if (
        24.5 <= lat <= 25.5
        and 66.5 <= lon <= 67.8
    ):
        return "karachi"

    if (
        31.0 <= lat <= 32.0
        and 73.5 <= lon <= 74.5
    ):
        return "lahore"

    if (
        29.5 <= lat <= 31.0
        and 68.0 <= lon <= 69.5
    ):
        return "multan"

    return "default"


def get_soil(
    lat: Optional[float],
    lon: Optional[float],
) -> dict[str, Any]:

    region = _region_from_coords(
        lat,
        lon,
    )

    with connect_db() as db:
        row = db.execute(
            """
            SELECT *
            FROM soil_profiles
            WHERE region_key=?
            """,
            (region,),
        ).fetchone()

    if not row:
        return {
            "source": "unavailable",
            "region": region,
        }

    result = dict(row)
    result["source"] = "local-demo-dataset"

    return result


# ============================================================
# Phase 6 — Context + Recommendation Engine
# ============================================================


def _severity_from_health(
    health: float,
) -> str:

    if health < 45:
        return "urgent"

    if health < 70:
        return "high"

    if health < 85:
        return "medium"

    return "low"


def _normalise_status(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip().lower()


def build_recommendation(
    farm: dict[str, Any],
    analysis: dict[str, Any],
    weather: dict[str, Any],
    soil: dict[str, Any],
) -> dict[str, Any]:

    crop = get_crop(
        farm["crop"]
    )

    health = float(
        analysis.get(
            "overall_health_pct",
            0,
        )
    )

    severity = _severity_from_health(
        health
    )

    evidence: list[str] = []
    hypotheses: list[dict[str, Any]] = []

    temp = weather.get(
        "temperature_c"
    )

    rain = weather.get(
        "rainfall_mm"
    )

    humidity = weather.get(
        "humidity_pct"
    )

    if crop:

        if (
            temp is not None
            and temp > crop["max_temp_c"]
        ):
            evidence.append(
                "Temperature is above the typical "
                f"{crop['name']} range."
            )

        if (
            rain is not None
            and rain <= 1
        ):
            evidence.append(
                "Very little current rainfall "
                "was recorded."
            )

        if (
            soil.get(
                "water_retention"
            )
            == "low"
        ):
            evidence.append(
                "The available soil profile "
                "has low water retention."
            )

        if (
            soil.get("drainage")
            in ("poor", "slow")
            and rain
            and rain > 10
        ):
            evidence.append(
                "The soil profile has slow drainage "
                "while rainfall is elevated."
            )

    dry_cells = sum(
        1
        for cell in analysis.get(
            "cells",
            [],
        )
        if _normalise_status(
            cell.get("status")
        )
        == "dry"
    )

    disease_cells = sum(
        1
        for cell in analysis.get(
            "cells",
            [],
        )
        if _normalise_status(
            cell.get("status")
        )
        == "disease"
    )

    pest_cells = sum(
        1
        for cell in analysis.get(
            "cells",
            [],
        )
        if _normalise_status(
            cell.get("status")
        )
        == "pest"
    )

    if dry_cells:
        evidence.append(
            f"{dry_cells} analyzed zone(s) "
            "were classified as dry."
        )

    if disease_cells:
        evidence.append(
            f"{disease_cells} analyzed zone(s) "
            "were classified with possible "
            "disease stress."
        )

    if pest_cells:
        evidence.append(
            f"{pest_cells} analyzed zone(s) "
            "were classified with possible "
            "pest stress."
        )

    water_score = 0

    if dry_cells:
        water_score += 40

    if (
        temp is not None
        and crop
        and temp > crop["ideal_temp_c"] + 7
    ):
        water_score += 25

    if (
        rain is not None
        and rain <= 1
    ):
        water_score += 20

    if (
        soil.get(
            "water_retention"
        )
        == "low"
    ):
        water_score += 15

    if water_score:

        confidence = min(
            95,
            40 + water_score,
        )

        hypotheses.append(
            {
                "cause": "possible water stress",
                "confidence_pct": confidence,
                "evidence": evidence[:],
                "action": (
                    "Check irrigation and water "
                    "distribution in the affected zones."
                ),
            }
        )

    if disease_cells:

        hypotheses.append(
            {
                "cause": "possible disease stress",
                "confidence_pct": min(
                    85,
                    45 + disease_cells * 10,
                ),
                "evidence": [
                    f"{disease_cells} zone(s) show "
                    "a disease-like classification."
                ],
                "action": (
                    "Inspect affected plants closely; "
                    "seek expert/agronomist advice "
                    "before applying treatment."
                ),
            }
        )

    if pest_cells:

        hypotheses.append(
            {
                "cause": "possible pest pressure",
                "confidence_pct": min(
                    85,
                    45 + pest_cells * 10,
                ),
                "evidence": [
                    f"{pest_cells} zone(s) show "
                    "a pest-like classification."
                ],
                "action": (
                    "Inspect affected zones for visible "
                    "pest damage before choosing a control method."
                ),
            }
        )

    if not hypotheses:

        hypotheses.append(
            {
                "cause": "no strong cause identified",
                "confidence_pct": max(
                    25,
                    min(
                        80,
                        health,
                    ),
                ),
                "evidence": (
                    evidence
                    or [
                        "The available scan/context data "
                        "does not strongly support one cause."
                    ]
                ),
                "action": (
                    "Continue monitoring and rescan "
                    "if the affected area changes."
                ),
            }
        )

    primary = max(
        hypotheses,
        key=lambda item: item[
            "confidence_pct"
        ],
    )

    rescan_hours = (
        48
        if severity in ("low", "medium")
        else 24
    )

    return {
        "status": (
            "attention"
            if severity != "low"
            else "monitor"
        ),
        "severity": severity,
        "possible_cause": primary[
            "cause"
        ],
        "confidence_pct": primary[
            "confidence_pct"
        ],
        "evidence": primary[
            "evidence"
        ],
        "recommended_action": primary[
            "action"
        ],
        "rescan_after_hours": rescan_hours,
        "hypotheses": hypotheses,
        "limitations": [
            "This is a decision-support recommendation, "
            "not a confirmed crop diagnosis.",
            "Image classifications and environmental data "
            "should be verified in the field for serious issues.",
        ],
    }


# ============================================================
# Phase 7 — LLM-ready structured contract
# ============================================================


def build_llm_payload(
    farm: dict[str, Any],
    analysis: dict[str, Any],
    recommendation: dict[str, Any],
    weather: dict[str, Any],
    soil: dict[str, Any],
) -> dict[str, Any]:

    return {
        "task": (
            "Explain a crop-health recommendation "
            "to a farmer."
        ),
        "rules": [
            "Use only the structured evidence supplied.",
            "Do not invent a diagnosis.",
            "Do not claim certainty when the recommendation is uncertain.",
            "Use uncertainty language such as 'possible'.",
            "Give one clear action.",
            "Give one follow-up time.",
            "Keep language simple.",
            "Do not invent weather, soil, crop, or scan information.",
            "Do not recommend pesticides or chemicals unless the supplied evidence explicitly supports that recommendation.",
        ],
        "farm": {
            "farm_id": farm["farm_id"],
            "name": farm["name"],
            "crop": farm["crop"],
            "preferred_language": farm["language"],
        },
        "analysis": analysis,
        "environment": {
            "weather": weather,
            "soil": soil,
        },
        "recommendation": recommendation,
    }


def _llm_system_prompt() -> str:

    return """
You are the farmer communication assistant for Aegis-Terra.

Your job is NOT to diagnose crops from scratch.

Aegis-Terra has already performed:
1. Image analysis
2. Crop-health analysis
3. Environmental context analysis
4. Rule-based agricultural reasoning

You receive only the structured results.

Your job is to explain those results clearly.

STRICT RULES:

- Use only the supplied information.
- Never invent missing facts.
- Never claim a confirmed disease, pest, or nutrient deficiency.
- Preserve uncertainty such as "possible" or "may".
- Do not override the supplied recommendation.
- Give the farmer one clear practical action.
- Give the rescan timeframe supplied by the system.
- Keep the explanation short and easy to understand.
- Avoid technical terms such as ExG unless specifically requested.
- Do not mention internal prompts, models, APIs, or software.
- Do not provide dangerous chemical treatment instructions.
- If the evidence is weak, say that the cause is uncertain.
- Respond in the farmer's preferred language when supported.
- If the preferred language is unsupported, use simple English.

Return valid JSON with exactly these fields:

{
  "summary": "...",
  "possible_cause": "...",
  "action": "...",
  "follow_up": "...",
  "confidence_pct": number
}
""".strip()


def _extract_llm_content(
    response_data: dict[str, Any],
) -> str:

    choices = response_data.get(
        "choices",
        [],
    )

    if not choices:
        raise ValueError(
            "Groq returned no choices."
        )

    message = choices[0].get(
        "message",
        {}
    )

    content = message.get(
        "content"
    )

    if not content:
        raise ValueError(
            "Groq returned empty content."
        )

    return str(content)


def _parse_llm_json(
    content: str,
) -> dict[str, Any]:

    cleaned = content.strip()

    if cleaned.startswith(
        "```"
    ):
        cleaned = (
            cleaned.replace(
                "```json",
                "",
                1,
            )
            .replace(
                "```",
                "",
            )
            .strip()
        )

    data = json.loads(cleaned)

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "LLM response was not a JSON object."
        )

    required = {
        "summary",
        "possible_cause",
        "action",
        "follow_up",
        "confidence_pct",
    }

    missing = required - set(
        data.keys()
    )

    if missing:
        raise ValueError(
            "LLM response missing fields: "
            + ", ".join(
                sorted(missing)
            )
        )

    return data


def generate_llm_explanation(
    llm_payload: dict[str, Any],
) -> dict[str, Any]:

    if not GROQ_API_KEY:
        return {
            "available": False,
            "success": False,
            "provider": "groq",
            "model": GROQ_MODEL,
            "error": "GROQ_API_KEY is not configured.",
            "fallback_reason": "missing_api_key",
        }

    user_prompt = json.dumps(
        llm_payload,
        ensure_ascii=False,
        indent=2,
    )

    request_body = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": _llm_system_prompt(),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": 0.2,
        "max_completion_tokens": 500,
        "response_format": {
            "type": "json_object"
        },
    }

    request = urllib.request.Request(
        GROQ_API_URL,
        data=json.dumps(
            request_body
        ).encode("utf-8"),
        headers={
            "Authorization": (
                f"Bearer {GROQ_API_KEY}"
            ),
            "Content-Type": (
                "application/json"
            ),
            "User-Agent": (
                "Aegis-Terra/1.0"
            ),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=GROQ_TIMEOUT_SECONDS,
        ) as response:

            response_data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        content = _extract_llm_content(
            response_data
        )

        parsed = _parse_llm_json(
            content
        )

        return {
            "available": True,
            "success": True,
            "provider": "groq",
            "model": GROQ_MODEL,
            "response": parsed,
        }

    except Exception as exc:

        logger.exception(
            "Groq LLM request failed."
        )

        return {
            "available": True,
            "success": False,
            "provider": "groq",
            "model": GROQ_MODEL,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
            "fallback_reason": "llm_request_failed",
        }


def build_llm_or_fallback(
    farm: dict[str, Any],
    analysis: dict[str, Any],
    recommendation: dict[str, Any],
    weather: dict[str, Any],
    soil: dict[str, Any],
) -> dict[str, Any]:

    payload = build_llm_payload(
        farm,
        analysis,
        recommendation,
        weather,
        soil,
    )

    llm_result = generate_llm_explanation(
        payload
    )

    if llm_result["success"]:
        return {
            **llm_result,
            "fallback_used": False,
            "structured_input": payload,
        }

    fallback_text = farmer_message(
        recommendation,
        farm["language"],
    )

    return {
        **llm_result,
        "fallback_used": True,
        "structured_input": payload,
        "response": {
            "summary": fallback_text,
            "possible_cause": recommendation[
                "possible_cause"
            ],
            "action": recommendation[
                "recommended_action"
            ],
            "follow_up": (
                "Rescan in about "
                f"{recommendation['rescan_after_hours']} "
                "hours."
            ),
            "confidence_pct": recommendation[
                "confidence_pct"
            ],
        },
    }


# ============================================================
# Phase 8 — Farmer-friendly text + voice-ready response
# ============================================================


LANGUAGE_TEMPLATES = {
    "english": {
        "water": (
            "This area may not be getting enough water. "
            "Please check irrigation in the affected zone."
        ),
        "disease": (
            "This area shows possible disease stress. "
            "Please inspect the plants closely and "
            "consider expert advice."
        ),
        "pest": (
            "This area shows possible pest pressure. "
            "Please inspect the affected plants for "
            "visible pest damage."
        ),
        "monitor": (
            "The crop looks mostly healthy. "
            "Keep monitoring and rescan if the "
            "condition changes."
        ),
    },
    "urdu": {
        "water": (
            "اس علاقے کو شاید مناسب پانی نہیں مل رہا۔ "
            "متاثرہ حصے کی آبپاشی چیک کریں۔"
        ),
        "disease": (
            "اس علاقے میں بیماری کے ممکنہ آثار ہیں۔ "
            "پودوں کا قریب سے معائنہ کریں اور ضرورت ہو "
            "تو ماہر سے مشورہ کریں۔"
        ),
        "pest": (
            "اس علاقے میں کیڑوں کا ممکنہ دباؤ ہے۔ "
            "متاثرہ پودوں کو قریب سے چیک کریں۔"
        ),
        "monitor": (
            "فصل زیادہ تر صحت مند نظر آ رہی ہے۔ "
            "نگرانی جاری رکھیں اور حالت بدلنے پر "
            "دوبارہ اسکین کریں۔"
        ),
    },
}


def farmer_message(
    recommendation: dict[str, Any],
    language: str,
) -> str:

    lang = language.strip().lower()

    templates = LANGUAGE_TEMPLATES.get(
        lang,
        LANGUAGE_TEMPLATES["english"],
    )

    cause = recommendation[
        "possible_cause"
    ]

    if "water" in cause:
        base = templates["water"]

    elif "disease" in cause:
        base = templates["disease"]

    elif "pest" in cause:
        base = templates["pest"]

    else:
        base = templates["monitor"]

    return (
        f"{base} "
        f"Rescan the area in about "
        f"{recommendation['rescan_after_hours']} hours."
    )


# ============================================================
# Phase 10 — Scans, history, alerts
# ============================================================


def save_scan(
    farm_id: str,
    analysis: dict[str, Any],
    recommendation: dict[str, Any],
) -> int:

    with connect_db() as db:

        cur = db.execute(
            """
            INSERT INTO scans
            (
                farm_id,
                scan_time,
                overall_health_pct,
                overall_status,
                analysis_json,
                recommendation_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                farm_id,
                now_iso(),
                float(
                    analysis.get(
                        "overall_health_pct",
                        0,
                    )
                ),
                str(
                    analysis.get(
                        "overall_status",
                        "unknown",
                    )
                ),
                json.dumps(
                    analysis
                ),
                json.dumps(
                    recommendation
                ),
            ),
        )

        scan_id = int(
            cur.lastrowid
        )

        for cell in analysis.get(
            "cells",
            [],
        ):

            status = _normalise_status(
                cell.get("status")
            )

            if status not in (
                "dry",
                "disease",
                "pest",
            ):
                continue

            severity = (
                "urgent"
                if status in (
                    "disease",
                    "pest",
                )
                else "high"
            )

            zone = str(
                cell.get("id")
                or cell.get("cell")
                or "unknown"
            )

            db.execute(
                """
                INSERT INTO alerts
                (
                    farm_id,
                    scan_id,
                    zone_id,
                    severity,
                    title,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    farm_id,
                    scan_id,
                    zone,
                    severity,
                    (
                        f"{status.title()} "
                        f"risk in {zone}"
                    ),
                    (
                        f"{zone} was classified "
                        f"as possible {status} stress. "
                        "Recommended action: "
                        f"{cell.get('recommended_action') or 'Inspect the zone.'}"
                    ),
                    now_iso(),
                ),
            )

    return scan_id


def compare_with_previous(
    farm_id: str,
    current_health: float,
) -> Optional[dict[str, Any]]:

    with connect_db() as db:

        row = db.execute(
            """
            SELECT
                overall_health_pct,
                scan_time
            FROM scans
            WHERE farm_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (farm_id,),
        ).fetchone()

    if not row:
        return None

    delta = (
        current_health
        - float(
            row["overall_health_pct"]
        )
    )

    return {
        "previous_health_pct": row[
            "overall_health_pct"
        ],
        "current_health_pct": current_health,
        "change_pct_points": round(
            delta,
            2,
        ),
        "trend": (
            "improved"
            if delta > 2
            else (
                "deteriorated"
                if delta < -2
                else "stable"
            )
        ),
        "previous_scan_time": row[
            "scan_time"
        ],
    }


# ============================================================
# Startup
# ============================================================


@router.on_event("startup")
def startup() -> None:
    init_db()
    seed_knowledge_base()


# ============================================================
# Routes
# ============================================================


@router.get("/status")
def intelligence_status() -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        crops = db.execute(
            """
            SELECT COUNT(*) AS n
            FROM crops
            """
        ).fetchone()["n"]

        soils = db.execute(
            """
            SELECT COUNT(*) AS n
            FROM soil_profiles
            """
        ).fetchone()["n"]

    return {
        "module": (
            "Aegis-Terra Intelligence Layer"
        ),
        "phases": "3-10",
        "local_kb": True,
        "crops": crops,
        "soil_profiles": soils,
        "offline_fallback": True,
        "llm": {
            "provider": "groq",
            "configured": bool(
                GROQ_API_KEY
            ),
            "model": GROQ_MODEL,
        },
    }


@router.get("/crops")
def list_crops() -> list[dict[str, Any]]:

    init_db()

    with connect_db() as db:

        rows = db.execute(
            """
            SELECT *
            FROM crops
            ORDER BY name
            """
        ).fetchall()

    return [
        _decode_crop(row)
        for row in rows
    ]


@router.get(
    "/crops/{crop_name}"
)
def crop_details(
    crop_name: str,
) -> dict[str, Any]:

    init_db()

    crop = get_crop(
        crop_name
    )

    if not crop:
        raise HTTPException(
            404,
            "Crop not found in local agricultural knowledge base.",
        )

    return crop


@router.post("/farms")
def upsert_farm(
    farm: FarmUpsert,
) -> dict[str, Any]:

    init_db()

    timestamp = now_iso()

    with connect_db() as db:

        db.execute(
            """
            INSERT INTO farms
            (
                farm_id,
                name,
                crop,
                language,
                latitude,
                longitude,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(farm_id) DO UPDATE SET
                name=excluded.name,
                crop=excluded.crop,
                language=excluded.language,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                updated_at=excluded.updated_at
            """,
            (
                farm.farm_id,
                farm.name,
                farm.crop,
                farm.language,
                farm.latitude,
                farm.longitude,
                timestamp,
                timestamp,
            ),
        )

    return {
        "message": "Farm profile saved.",
        "farm": farm.model_dump(),
    }


@router.get(
    "/farms/{farm_id}/context"
)
def farm_context(
    farm_id: str,
) -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        row = db.execute(
            """
            SELECT *
            FROM farms
            WHERE farm_id=?
            """,
            (farm_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            404,
            "Farm not found.",
        )

    farm = dict(row)

    if (
        farm["latitude"] is not None
        and farm["longitude"] is not None
    ):
        weather = fetch_weather(
            farm["latitude"],
            farm["longitude"],
        )
    else:
        weather = {
            "source": "unavailable"
        }

    soil = get_soil(
        farm["latitude"],
        farm["longitude"],
    )

    crop = get_crop(
        farm["crop"]
    )

    return {
        "farm": farm,
        "crop": crop,
        "weather": weather,
        "soil": soil,
    }


@router.post("/recommend")
def recommend(
    payload: RecommendationInput,
) -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        row = db.execute(
            """
            SELECT *
            FROM farms
            WHERE farm_id=?
            """,
            (payload.farm_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            404,
            "Farm not found. Save the farm profile first.",
        )

    farm = dict(row)

    weather = (
        payload.weather
        or (
            fetch_weather(
                farm["latitude"],
                farm["longitude"],
            )
            if (
                farm["latitude"] is not None
                and farm["longitude"] is not None
            )
            else {
                "source": "unavailable"
            }
        )
    )

    soil = (
        payload.soil
        or get_soil(
            farm["latitude"],
            farm["longitude"],
        )
    )

    recommendation = build_recommendation(
        farm,
        payload.analysis,
        weather,
        soil,
    )

    llm_payload = build_llm_payload(
        farm,
        payload.analysis,
        recommendation,
        weather,
        soil,
    )

    llm_result = build_llm_or_fallback(
        farm,
        payload.analysis,
        recommendation,
        weather,
        soil,
    )

    fallback_text = farmer_message(
        recommendation,
        farm["language"],
    )

    comparison = compare_with_previous(
        farm["farm_id"],
        float(
            payload.analysis.get(
                "overall_health_pct",
                0,
            )
        ),
    )

    return {
        "farm": farm,
        "weather": weather,
        "soil": soil,
        "recommendation": recommendation,
        "farmer_message": fallback_text,
        "llm": llm_result,
        "llm_payload": llm_payload,
        "comparison": comparison,
        "voice_ready_text": (
            llm_result.get(
                "response",
                {},
            ).get(
                "summary",
                fallback_text,
            )
        ),
    }


# ============================================================
# Phase 7 — Dedicated LLM endpoint
# ============================================================


@router.post(
    "/llm/explain"
)
def llm_explain(
    payload: LLMExplainInput,
) -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        row = db.execute(
            """
            SELECT *
            FROM farms
            WHERE farm_id=?
            """,
            (payload.farm_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            404,
            "Farm not found.",
        )

    farm = dict(row)

    weather = (
        payload.weather
        or (
            fetch_weather(
                farm["latitude"],
                farm["longitude"],
            )
            if (
                farm["latitude"] is not None
                and farm["longitude"] is not None
            )
            else {
                "source": "unavailable"
            }
        )
    )

    soil = (
        payload.soil
        or get_soil(
            farm["latitude"],
            farm["longitude"],
        )
    )

    result = build_llm_or_fallback(
        farm,
        payload.analysis,
        payload.recommendation,
        weather,
        soil,
    )

    return result


# ============================================================
# Phase 10 — Scan recording
# ============================================================


@router.post("/scans")
def record_scan(
    payload: ScanInput,
) -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        row = db.execute(
            """
            SELECT *
            FROM farms
            WHERE farm_id=?
            """,
            (payload.farm_id,),
        ).fetchone()

    if not row:
        raise HTTPException(
            404,
            "Farm not found.",
        )

    farm = dict(row)

    weather = (
        fetch_weather(
            farm["latitude"],
            farm["longitude"],
        )
        if (
            farm["latitude"] is not None
            and farm["longitude"] is not None
        )
        else {
            "source": "unavailable"
        }
    )

    soil = get_soil(
        farm["latitude"],
        farm["longitude"],
    )

    analysis = payload.model_dump(
        exclude={
            "farm_id"
        }
    )

    recommendation = build_recommendation(
        farm,
        analysis,
        weather,
        soil,
    )

    scan_id = save_scan(
        payload.farm_id,
        analysis,
        recommendation,
    )

    comparison = compare_with_previous(
        payload.farm_id,
        payload.overall_health_pct,
    )

    return {
        "scan_id": scan_id,
        "recommendation": recommendation,
        "comparison": comparison,
        "farmer_message": farmer_message(
            recommendation,
            farm["language"],
        ),
    }


@router.get(
    "/farms/{farm_id}/history"
)
def farm_history(
    farm_id: str,
) -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        scans = db.execute(
            """
            SELECT
                id,
                scan_time,
                overall_health_pct,
                overall_status,
                recommendation_json
            FROM scans
            WHERE farm_id=?
            ORDER BY id DESC
            """,
            (farm_id,),
        ).fetchall()

        alerts = db.execute(
            """
            SELECT
                id,
                scan_id,
                zone_id,
                severity,
                title,
                message,
                acknowledged,
                created_at
            FROM alerts
            WHERE farm_id=?
            ORDER BY id DESC
            """,
            (farm_id,),
        ).fetchall()

    return {
        "scans": [
            {
                **dict(scan),
                "recommendation": (
                    json.loads(
                        scan[
                            "recommendation_json"
                        ]
                    )
                    if scan[
                        "recommendation_json"
                    ]
                    else None
                ),
            }
            for scan in scans
        ],
        "alerts": [
            dict(alert)
            for alert in alerts
        ],
    }


@router.post(
    "/alerts/{alert_id}/acknowledge"
)
def acknowledge_alert(
    alert_id: int,
) -> dict[str, Any]:

    init_db()

    with connect_db() as db:

        cur = db.execute(
            """
            UPDATE alerts
            SET acknowledged=1
            WHERE id=?
            """,
            (alert_id,),
        )

    if cur.rowcount == 0:
        raise HTTPException(
            404,
            "Alert not found.",
        )

    return {
        "message": "Alert acknowledged.",
        "alert_id": alert_id,
    }


# ============================================================
# Ensure local database exists when imported
# ============================================================

init_db()
seed_knowledge_base()