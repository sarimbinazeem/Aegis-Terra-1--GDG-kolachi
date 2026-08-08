"""
Aegis-Terra - Local Agricultural Knowledge Base
Phase 3

Responsibilities:
- Create the local SQLite agricultural database.
- Seed crop knowledge.
- Retrieve crop requirements.
- Retrieve growth-stage information.
- Retrieve common stress conditions.
- Provide structured agricultural context for later phases.

This module intentionally uses only Python standard-library modules.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

APP_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "agriculture.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection() -> sqlite3.Connection:
    """
    Create a SQLite connection.

    row_factory allows rows to behave like dictionaries.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# DATABASE SCHEMA
# ============================================================

SCHEMA = """
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    scientific_name TEXT,

    description TEXT,

    preferred_temperature_min_c REAL,
    preferred_temperature_max_c REAL,

    water_requirement TEXT,

    soil_texture TEXT,

    soil_drainage TEXT,

    water_retention TEXT,

    ph_min REAL,
    ph_max REAL,

    source_type TEXT DEFAULT 'local_demo_knowledge',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS crop_growth_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    crop_id INTEGER NOT NULL,

    stage_name TEXT NOT NULL,

    stage_order INTEGER NOT NULL,

    description TEXT,

    water_requirement TEXT,

    temperature_note TEXT,

    FOREIGN KEY (crop_id)
        REFERENCES crops(id),

    UNIQUE(crop_id, stage_name)
);


CREATE TABLE IF NOT EXISTS crop_stress_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    crop_id INTEGER NOT NULL,

    stress_type TEXT NOT NULL,

    trigger_condition TEXT NOT NULL,

    symptoms TEXT NOT NULL,

    recommended_action TEXT NOT NULL,

    severity_default TEXT DEFAULT 'medium',

    FOREIGN KEY (crop_id)
        REFERENCES crops(id)
);


CREATE INDEX IF NOT EXISTS idx_crop_name
ON crops(name);


CREATE INDEX IF NOT EXISTS idx_growth_crop
ON crop_growth_stages(crop_id);


CREATE INDEX IF NOT EXISTS idx_stress_crop
ON crop_stress_conditions(crop_id);
"""


# ============================================================
# SEED DATA
# ============================================================

CROPS: list[dict[str, Any]] = [

    {
        "name": "wheat",
        "scientific_name": "Triticum aestivum",
        "description": (
            "A major cereal crop commonly grown during the cool season. "
            "Water demand varies significantly with growth stage."
        ),
        "temperature_min": 10,
        "temperature_max": 25,
        "water_requirement": "moderate",
        "soil_texture": "loam to sandy loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 6.0,
        "ph_max": 7.5,

        "stages": [
            {
                "name": "germination",
                "order": 1,
                "description": "Seed germination and early establishment.",
                "water": "moderate",
                "temperature": "Cool to mild conditions.",
            },
            {
                "name": "tillering",
                "order": 2,
                "description": "Development of tillers and vegetative growth.",
                "water": "moderate",
                "temperature": "Cool to mild conditions.",
            },
            {
                "name": "stem_extension",
                "order": 3,
                "description": "Rapid stem and canopy development.",
                "water": "moderate to high",
                "temperature": "Mild conditions preferred.",
            },
            {
                "name": "heading",
                "order": 4,
                "description": "Ear/head emergence and reproductive development.",
                "water": "high",
                "temperature": "Avoid severe heat stress.",
            },
            {
                "name": "grain_filling",
                "order": 5,
                "description": "Grain development and filling.",
                "water": "moderate to high",
                "temperature": "Excessive heat can increase stress.",
            },
            {
                "name": "maturity",
                "order": 6,
                "description": "Grain reaches physiological maturity.",
                "water": "low",
                "temperature": "Dry conditions are increasingly tolerated.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Low available soil moisture combined with high temperature or low rainfall.",
                "symptoms": "Reduced vigor, leaf rolling, yellowing or reduced canopy development.",
                "action": "Check irrigation coverage and soil moisture in the affected zone.",
                "severity": "medium",
            },
            {
                "type": "heat_stress",
                "trigger": "Temperature substantially above the preferred range during sensitive stages.",
                "symptoms": "Reduced vigor and possible reproductive stress.",
                "action": "Check water availability and crop stage before making irrigation decisions.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "rice",
        "scientific_name": "Oryza sativa",
        "description": "A warm-season cereal crop with relatively high water requirements.",
        "temperature_min": 20,
        "temperature_max": 35,
        "water_requirement": "high",
        "soil_texture": "clay loam to loam",
        "soil_drainage": "moderate",
        "water_retention": "high",
        "ph_min": 5.5,
        "ph_max": 7.0,

        "stages": [
            {
                "name": "germination",
                "order": 1,
                "description": "Seed germination and establishment.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf and tiller development.",
                "water": "high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "reproductive",
                "order": 3,
                "description": "Panicle development and flowering.",
                "water": "high",
                "temperature": "Avoid severe heat and moisture stress.",
            },
            {
                "name": "grain_filling",
                "order": 4,
                "description": "Grain development.",
                "water": "high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 5,
                "description": "Grain maturation.",
                "water": "moderate to low",
                "temperature": "Drying conditions become more suitable.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Insufficient available water during active vegetative or reproductive growth.",
                "symptoms": "Reduced canopy growth, leaf rolling and poor vigor.",
                "action": "Check water availability and irrigation distribution.",
                "severity": "high",
            },
            {
                "type": "heat_stress",
                "trigger": "Excessive temperatures around sensitive reproductive stages.",
                "symptoms": "Reduced vigor and possible reproductive damage.",
                "action": "Check irrigation and crop stage.",
                "severity": "high",
            },
        ],
    },

    {
        "name": "maize",
        "scientific_name": "Zea mays",
        "description": "A warm-season cereal requiring reliable moisture during key growth stages.",
        "temperature_min": 18,
        "temperature_max": 32,
        "water_requirement": "moderate to high",
        "soil_texture": "loam to sandy loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 5.8,
        "ph_max": 7.0,

        "stages": [
            {
                "name": "germination",
                "order": 1,
                "description": "Seed germination and emergence.",
                "water": "moderate",
                "temperature": "Warm soil conditions preferred.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Rapid leaf and stem development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "tasseling_silking",
                "order": 3,
                "description": "Flowering and pollination.",
                "water": "high",
                "temperature": "Avoid severe heat stress.",
            },
            {
                "name": "grain_filling",
                "order": 4,
                "description": "Kernel development.",
                "water": "moderate to high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 5,
                "description": "Dry-down and grain maturity.",
                "water": "low",
                "temperature": "Dry conditions increasingly tolerated.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Low soil moisture during vegetative or reproductive growth.",
                "symptoms": "Leaf rolling, reduced canopy and weak growth.",
                "action": "Check irrigation coverage and soil moisture.",
                "severity": "high",
            },
            {
                "type": "heat_stress",
                "trigger": "High temperature during flowering or grain formation.",
                "symptoms": "Reduced vigor and possible reproductive stress.",
                "action": "Check water availability and crop stage.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "cotton",
        "scientific_name": "Gossypium hirsutum",
        "description": "A warm-season fiber crop requiring careful water management during flowering and boll development.",
        "temperature_min": 21,
        "temperature_max": 35,
        "water_requirement": "moderate to high",
        "soil_texture": "loam to clay loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate to high",
        "ph_min": 5.5,
        "ph_max": 8.0,

        "stages": [
            {
                "name": "germination",
                "order": 1,
                "description": "Seed emergence and establishment.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf, branch and canopy development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "flowering",
                "order": 3,
                "description": "Flower production.",
                "water": "high",
                "temperature": "Avoid severe heat and moisture stress.",
            },
            {
                "name": "boll_development",
                "order": 4,
                "description": "Boll growth and fiber development.",
                "water": "moderate to high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 5,
                "description": "Boll opening and crop maturation.",
                "water": "low",
                "temperature": "Dry conditions preferred near harvest.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Low soil moisture during flowering or boll development.",
                "symptoms": "Reduced vigor, leaf stress and poor reproductive development.",
                "action": "Check irrigation and soil moisture.",
                "severity": "high",
            },
            {
                "type": "pest_stress",
                "trigger": "Possible pest activity affecting leaves or reproductive structures.",
                "symptoms": "Localized damage, abnormal leaves or damaged reproductive structures.",
                "action": "Inspect affected plants closely for pest evidence.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "sugarcane",
        "scientific_name": "Saccharum officinarum",
        "description": "A long-duration warm-season crop with substantial water requirements.",
        "temperature_min": 20,
        "temperature_max": 35,
        "water_requirement": "high",
        "soil_texture": "loam to clay loam",
        "soil_drainage": "well drained to moderate",
        "water_retention": "high",
        "ph_min": 6.0,
        "ph_max": 7.5,

        "stages": [
            {
                "name": "establishment",
                "order": 1,
                "description": "Setts establish roots and shoots.",
                "water": "moderate to high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "tillering",
                "order": 2,
                "description": "Multiple stalks develop.",
                "water": "high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "grand_growth",
                "order": 3,
                "description": "Rapid stalk and biomass accumulation.",
                "water": "high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 4,
                "description": "Sugar accumulation and maturation.",
                "water": "moderate",
                "temperature": "Warm and relatively dry conditions become favorable.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Insufficient soil moisture during active growth.",
                "symptoms": "Reduced leaf development and weak canopy.",
                "action": "Check irrigation and soil moisture.",
                "severity": "high",
            },
        ],
    },

    {
        "name": "potato",
        "scientific_name": "Solanum tuberosum",
        "description": "A cool-to-mild season tuber crop sensitive to irregular moisture.",
        "temperature_min": 15,
        "temperature_max": 25,
        "water_requirement": "moderate",
        "soil_texture": "sandy loam to loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 5.0,
        "ph_max": 6.5,

        "stages": [
            {
                "name": "sprouting",
                "order": 1,
                "description": "Sprout emergence and early establishment.",
                "water": "moderate",
                "temperature": "Cool to mild conditions.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf and canopy development.",
                "water": "moderate",
                "temperature": "Cool to mild conditions.",
            },
            {
                "name": "tuber_initiation",
                "order": 3,
                "description": "Beginning of tuber formation.",
                "water": "moderate to high",
                "temperature": "Avoid excessive heat.",
            },
            {
                "name": "tuber_bulking",
                "order": 4,
                "description": "Rapid tuber growth.",
                "water": "high",
                "temperature": "Mild conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 5,
                "description": "Tuber maturation and crop senescence.",
                "water": "moderate to low",
                "temperature": "Cooler conditions preferred.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Insufficient or highly irregular soil moisture.",
                "symptoms": "Reduced canopy vigor and possible tuber development problems.",
                "action": "Check soil moisture consistency and irrigation.",
                "severity": "medium",
            },
            {
                "type": "heat_stress",
                "trigger": "Sustained temperatures above the preferred range.",
                "symptoms": "Reduced canopy vigor and impaired tuber development.",
                "action": "Check irrigation and field temperature conditions.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "tomato",
        "scientific_name": "Solanum lycopersicum",
        "description": "A warm-season vegetable crop requiring relatively consistent moisture.",
        "temperature_min": 18,
        "temperature_max": 30,
        "water_requirement": "moderate",
        "soil_texture": "loam to sandy loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 5.5,
        "ph_max": 7.0,

        "stages": [
            {
                "name": "seedling",
                "order": 1,
                "description": "Early seedling establishment.",
                "water": "moderate",
                "temperature": "Mild to warm conditions.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf and stem development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "flowering",
                "order": 3,
                "description": "Flower production and pollination.",
                "water": "moderate",
                "temperature": "Avoid severe heat.",
            },
            {
                "name": "fruit_development",
                "order": 4,
                "description": "Fruit growth and development.",
                "water": "moderate to high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "ripening",
                "order": 5,
                "description": "Fruit color and maturity development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Low or highly irregular soil moisture.",
                "symptoms": "Wilting, reduced growth and possible fruit-quality problems.",
                "action": "Check irrigation consistency and soil moisture.",
                "severity": "medium",
            },
            {
                "type": "pest_stress",
                "trigger": "Possible insect pressure in localized areas.",
                "symptoms": "Leaf damage, curling or localized plant decline.",
                "action": "Inspect affected plants for visible pest evidence.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "onion",
        "scientific_name": "Allium cepa",
        "description": "A bulb crop requiring good drainage and consistent moisture during bulb development.",
        "temperature_min": 13,
        "temperature_max": 25,
        "water_requirement": "moderate",
        "soil_texture": "sandy loam to loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 6.0,
        "ph_max": 7.0,

        "stages": [
            {
                "name": "germination",
                "order": 1,
                "description": "Seed germination and establishment.",
                "water": "moderate",
                "temperature": "Cool to mild conditions.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf development.",
                "water": "moderate",
                "temperature": "Cool to mild conditions.",
            },
            {
                "name": "bulbing",
                "order": 3,
                "description": "Bulb enlargement.",
                "water": "moderate to high",
                "temperature": "Mild conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 4,
                "description": "Bulb maturation and drying.",
                "water": "low",
                "temperature": "Dry conditions become favorable.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Insufficient moisture during active bulb development.",
                "symptoms": "Reduced leaf vigor and smaller bulb development.",
                "action": "Check irrigation and soil moisture.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "chili",
        "scientific_name": "Capsicum annuum",
        "description": "A warm-season vegetable crop requiring consistent moisture and warm temperatures.",
        "temperature_min": 18,
        "temperature_max": 32,
        "water_requirement": "moderate",
        "soil_texture": "loam to sandy loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 5.5,
        "ph_max": 7.0,

        "stages": [
            {
                "name": "seedling",
                "order": 1,
                "description": "Seedling establishment.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf and branch development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "flowering",
                "order": 3,
                "description": "Flower production.",
                "water": "moderate",
                "temperature": "Avoid severe heat.",
            },
            {
                "name": "fruiting",
                "order": 4,
                "description": "Fruit development.",
                "water": "moderate to high",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "maturity",
                "order": 5,
                "description": "Fruit maturation.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Low available soil moisture.",
                "symptoms": "Wilting and reduced growth.",
                "action": "Check irrigation and soil moisture.",
                "severity": "medium",
            },
            {
                "type": "pest_stress",
                "trigger": "Possible localized insect activity.",
                "symptoms": "Leaf curling, holes or localized damage.",
                "action": "Inspect affected plants for visible pests.",
                "severity": "medium",
            },
        ],
    },

    {
        "name": "okra",
        "scientific_name": "Abelmoschus esculentus",
        "description": "A warm-season vegetable crop suited to warm growing conditions.",
        "temperature_min": 21,
        "temperature_max": 35,
        "water_requirement": "moderate",
        "soil_texture": "loam to sandy loam",
        "soil_drainage": "well drained",
        "water_retention": "moderate",
        "ph_min": 6.0,
        "ph_max": 7.5,

        "stages": [
            {
                "name": "germination",
                "order": 1,
                "description": "Seed germination and emergence.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "vegetative",
                "order": 2,
                "description": "Leaf and stem development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "flowering",
                "order": 3,
                "description": "Flower production.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
            {
                "name": "fruiting",
                "order": 4,
                "description": "Pod development.",
                "water": "moderate",
                "temperature": "Warm conditions preferred.",
            },
        ],

        "stresses": [
            {
                "type": "water_stress",
                "trigger": "Insufficient moisture during flowering or fruiting.",
                "symptoms": "Wilting and reduced plant vigor.",
                "action": "Check irrigation and soil moisture.",
                "severity": "medium",
            },
            {
                "type": "heat_stress",
                "trigger": "Sustained excessive temperature.",
                "symptoms": "Reduced vigor or reproductive stress.",
                "action": "Check water availability and field conditions.",
                "severity": "medium",
            },
        ],
    },
]


# ============================================================
# INITIALIZATION
# ============================================================

def initialize_database() -> None:
    """
    Create all Phase 3 tables and seed them if empty.
    """

    connection = get_connection()

    try:

        connection.executescript(SCHEMA)

        crop_count = connection.execute(
            "SELECT COUNT(*) AS count FROM crops"
        ).fetchone()["count"]

        if crop_count == 0:
            seed_database(connection)

        connection.commit()

    finally:
        connection.close()


# ============================================================
# SEED DATABASE
# ============================================================

def seed_database(
    connection: sqlite3.Connection,
) -> None:

    for crop in CROPS:

        cursor = connection.execute(
            """
            INSERT INTO crops (
                name,
                scientific_name,
                description,
                preferred_temperature_min_c,
                preferred_temperature_max_c,
                water_requirement,
                soil_texture,
                soil_drainage,
                water_retention,
                ph_min,
                ph_max,
                source_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                crop["name"],
                crop["scientific_name"],
                crop["description"],
                crop["temperature_min"],
                crop["temperature_max"],
                crop["water_requirement"],
                crop["soil_texture"],
                crop["soil_drainage"],
                crop["water_retention"],
                crop["ph_min"],
                crop["ph_max"],
                "local_demo_knowledge",
            ),
        )

        crop_id = cursor.lastrowid

        for stage in crop["stages"]:

            connection.execute(
                """
                INSERT INTO crop_growth_stages (
                    crop_id,
                    stage_name,
                    stage_order,
                    description,
                    water_requirement,
                    temperature_note
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    crop_id,
                    stage["name"],
                    stage["order"],
                    stage["description"],
                    stage["water"],
                    stage["temperature"],
                ),
            )

        for stress in crop["stresses"]:

            connection.execute(
                """
                INSERT INTO crop_stress_conditions (
                    crop_id,
                    stress_type,
                    trigger_condition,
                    symptoms,
                    recommended_action,
                    severity_default
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    crop_id,
                    stress["type"],
                    stress["trigger"],
                    stress["symptoms"],
                    stress["action"],
                    stress["severity"],
                ),
            )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_crop_name(
    crop_name: str,
) -> str:

    return (
        crop_name
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


# ============================================================
# CROP LIST
# ============================================================

def list_crops() -> list[dict[str, Any]]:

    initialize_database()

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                id,
                name,
                scientific_name,
                description,
                preferred_temperature_min_c,
                preferred_temperature_max_c,
                water_requirement,
                soil_texture,
                soil_drainage,
                water_retention,
                ph_min,
                ph_max,
                source_type
            FROM crops
            ORDER BY name
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# ============================================================
# GET CROP
# ============================================================

def get_crop(
    crop_name: str,
) -> dict[str, Any] | None:

    initialize_database()

    normalized = normalize_crop_name(crop_name)

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                id,
                name,
                scientific_name,
                description,
                preferred_temperature_min_c,
                preferred_temperature_max_c,
                water_requirement,
                soil_texture,
                soil_drainage,
                water_retention,
                ph_min,
                ph_max,
                source_type
            FROM crops
            WHERE lower(name) = ?
            """,
            (normalized,),
        ).fetchone()

        if row is None:
            return None

        crop = dict(row)

        crop["growth_stages"] = get_growth_stages_by_id(
            connection,
            crop["id"],
        )

        crop["stress_conditions"] = get_stresses_by_id(
            connection,
            crop["id"],
        )

        return crop

    finally:
        connection.close()


# ============================================================
# GROWTH STAGES
# ============================================================

def get_growth_stages_by_id(
    connection: sqlite3.Connection,
    crop_id: int,
) -> list[dict[str, Any]]:

    rows = connection.execute(
        """
        SELECT
            stage_name,
            stage_order,
            description,
            water_requirement,
            temperature_note
        FROM crop_growth_stages
        WHERE crop_id = ?
        ORDER BY stage_order
        """,
        (crop_id,),
    ).fetchall()

    return [dict(row) for row in rows]


def get_growth_stages(
    crop_name: str,
) -> list[dict[str, Any]]:

    crop = get_crop(crop_name)

    if crop is None:
        return []

    return crop["growth_stages"]


# ============================================================
# STRESS CONDITIONS
# ============================================================

def get_stresses_by_id(
    connection: sqlite3.Connection,
    crop_id: int,
) -> list[dict[str, Any]]:

    rows = connection.execute(
        """
        SELECT
            stress_type,
            trigger_condition,
            symptoms,
            recommended_action,
            severity_default
        FROM crop_stress_conditions
        WHERE crop_id = ?
        ORDER BY stress_type
        """,
        (crop_id,),
    ).fetchall()

    return [dict(row) for row in rows]


def get_stress_conditions(
    crop_name: str,
) -> list[dict[str, Any]]:

    crop = get_crop(crop_name)

    if crop is None:
        return []

    return crop["stress_conditions"]


# ============================================================
# AGRICULTURAL CONTEXT
# ============================================================

def get_agricultural_context(
    crop_name: str,
    growth_stage: str | None = None,
) -> dict[str, Any] | None:
    """
    Return the structured agricultural context that later phases
    will consume.

    This is intentionally structured so Phase 6 can combine it with:
        - image analysis
        - weather
        - soil
        - history
    """

    crop = get_crop(crop_name)

    if crop is None:
        return None

    selected_stage = None

    if growth_stage:

        normalized_stage = (
            growth_stage
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        for stage in crop["growth_stages"]:

            if stage["stage_name"] == normalized_stage:
                selected_stage = stage
                break

    return {
        "crop": {
            "name": crop["name"],
            "scientific_name": crop["scientific_name"],
            "description": crop["description"],
        },

        "environmental_requirements": {
            "temperature_c": {
                "min": crop[
                    "preferred_temperature_min_c"
                ],
                "max": crop[
                    "preferred_temperature_max_c"
                ],
            },

            "water_requirement":
                crop["water_requirement"],

            "soil_texture":
                crop["soil_texture"],

            "soil_drainage":
                crop["soil_drainage"],

            "water_retention":
                crop["water_retention"],

            "ph": {
                "min": crop["ph_min"],
                "max": crop["ph_max"],
            },
        },

        "growth_stage":
            selected_stage,

        "growth_stages":
            crop["growth_stages"],

        "known_stress_conditions":
            crop["stress_conditions"],

        "knowledge_source":
            crop["source_type"],
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def knowledge_base_status() -> dict[str, Any]:

    initialize_database()

    connection = get_connection()

    try:

        crop_count = connection.execute(
            "SELECT COUNT(*) AS count FROM crops"
        ).fetchone()["count"]

        stage_count = connection.execute(
            "SELECT COUNT(*) AS count FROM crop_growth_stages"
        ).fetchone()["count"]

        stress_count = connection.execute(
            "SELECT COUNT(*) AS count FROM crop_stress_conditions"
        ).fetchone()["count"]

        return {
            "status": "ready",
            "database": str(DATABASE_PATH),
            "crops": crop_count,
            "growth_stages": stage_count,
            "stress_conditions": stress_count,
        }

    finally:
        connection.close()