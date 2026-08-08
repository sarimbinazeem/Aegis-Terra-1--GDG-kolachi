from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "agriculture.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                scientific_name TEXT,
                description TEXT,
                min_temperature_c REAL,
                max_temperature_c REAL,
                min_rainfall_mm REAL,
                max_rainfall_mm REAL,
                min_ph REAL,
                max_ph REAL,
                water_requirement TEXT,
                preferred_soil_texture TEXT,
                water_retention TEXT,
                drainage TEXT
            );

            CREATE TABLE IF NOT EXISTS growth_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL,
                stage_name TEXT NOT NULL,
                duration_days INTEGER,
                min_temperature_c REAL,
                max_temperature_c REAL,
                water_requirement TEXT,
                notes TEXT,
                FOREIGN KEY (crop_id) REFERENCES crops(id)
            );

            CREATE TABLE IF NOT EXISTS stress_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL,
                condition_name TEXT NOT NULL,
                indicators TEXT,
                severity TEXT,
                recommendation TEXT,
                FOREIGN KEY (crop_id) REFERENCES crops(id)
            );

            CREATE TABLE IF NOT EXISTS soil_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                texture TEXT NOT NULL,
                ph_min REAL,
                ph_max REAL,
                water_retention TEXT,
                drainage TEXT,
                description TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_growth_crop
            ON growth_stages(crop_id);

            CREATE INDEX IF NOT EXISTS idx_stress_crop
            ON stress_conditions(crop_id);
            """
        )

        connection.commit()

    finally:
        connection.close()