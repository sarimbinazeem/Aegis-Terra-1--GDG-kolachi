from .database import get_connection


CROPS = [
    {
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "description": "Cool-season cereal crop.",
        "min_temperature_c": 10,
        "max_temperature_c": 25,
        "min_rainfall_mm": 300,
        "max_rainfall_mm": 900,
        "min_ph": 6.0,
        "max_ph": 7.5,
        "water_requirement": "moderate",
        "preferred_soil_texture": "loam",
        "water_retention": "moderate",
        "drainage": "good",
    },
    {
        "name": "Rice",
        "scientific_name": "Oryza sativa",
        "description": "Warm-season cereal crop requiring substantial water.",
        "min_temperature_c": 20,
        "max_temperature_c": 35,
        "min_rainfall_mm": 1000,
        "max_rainfall_mm": 2500,
        "min_ph": 5.5,
        "max_ph": 7.0,
        "water_requirement": "high",
        "preferred_soil_texture": "clay loam",
        "water_retention": "high",
        "drainage": "moderate",
    },
    {
        "name": "Maize",
        "scientific_name": "Zea mays",
        "description": "Warm-season cereal crop.",
        "min_temperature_c": 18,
        "max_temperature_c": 32,
        "min_rainfall_mm": 500,
        "max_rainfall_mm": 1200,
        "min_ph": 5.8,
        "max_ph": 7.0,
        "water_requirement": "moderate",
        "preferred_soil_texture": "loam",
        "water_retention": "moderate",
        "drainage": "good",
    },
    {
        "name": "Cotton",
        "scientific_name": "Gossypium hirsutum",
        "description": "Warm-season fiber crop.",
        "min_temperature_c": 21,
        "max_temperature_c": 35,
        "min_rainfall_mm": 500,
        "max_rainfall_mm": 1200,
        "min_ph": 5.5,
        "max_ph": 8.0,
        "water_requirement": "moderate",
        "preferred_soil_texture": "loam",
        "water_retention": "moderate",
        "drainage": "good",
    },
    {
        "name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "description": "Long-duration tropical and subtropical crop.",
        "min_temperature_c": 20,
        "max_temperature_c": 35,
        "min_rainfall_mm": 1100,
        "max_rainfall_mm": 2500,
        "min_ph": 6.0,
        "max_ph": 7.5,
        "water_requirement": "high",
        "preferred_soil_texture": "loam",
        "water_retention": "high",
        "drainage": "good",
    },
    {
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "description": "Warm-season vegetable crop.",
        "min_temperature_c": 18,
        "max_temperature_c": 30,
        "min_rainfall_mm": 400,
        "max_rainfall_mm": 800,
        "min_ph": 6.0,
        "max_ph": 6.8,
        "water_requirement": "moderate",
        "preferred_soil_texture": "sandy loam",
        "water_retention": "moderate",
        "drainage": "good",
    },
    {
        "name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "description": "Cool-season tuber crop.",
        "min_temperature_c": 15,
        "max_temperature_c": 25,
        "min_rainfall_mm": 500,
        "max_rainfall_mm": 700,
        "min_ph": 5.0,
        "max_ph": 6.5,
        "water_requirement": "moderate",
        "preferred_soil_texture": "sandy loam",
        "water_retention": "moderate",
        "drainage": "excellent",
    },
    {
        "name": "Chickpea",
        "scientific_name": "Cicer arietinum",
        "description": "Cool-season pulse crop.",
        "min_temperature_c": 15,
        "max_temperature_c": 30,
        "min_rainfall_mm": 300,
        "max_rainfall_mm": 600,
        "min_ph": 6.0,
        "max_ph": 8.0,
        "water_requirement": "low",
        "preferred_soil_texture": "loam",
        "water_retention": "moderate",
        "drainage": "good",
    },
]


GROWTH_STAGES = {
    "Wheat": [
        ("Germination", 10, 5, 20, "moderate"),
        ("Vegetative", 45, 10, 25, "moderate"),
        ("Flowering", 20, 12, 25, "high"),
        ("Grain Filling", 30, 15, 28, "moderate"),
        ("Maturity", 20, 15, 30, "low"),
    ],
    "Rice": [
        ("Germination", 10, 20, 35, "high"),
        ("Vegetative", 45, 20, 35, "high"),
        ("Flowering", 25, 22, 32, "high"),
        ("Grain Filling", 30, 20, 32, "high"),
        ("Maturity", 20, 18, 30, "moderate"),
    ],
    "Maize": [
        ("Germination", 7, 18, 30, "moderate"),
        ("Vegetative", 40, 18, 32, "moderate"),
        ("Flowering", 20, 20, 32, "high"),
        ("Grain Filling", 35, 18, 30, "moderate"),
        ("Maturity", 25, 18, 30, "low"),
    ],
    "Cotton": [
        ("Germination", 10, 21, 32, "moderate"),
        ("Vegetative", 45, 21, 35, "moderate"),
        ("Flowering", 30, 22, 35, "high"),
        ("Boll Development", 45, 20, 32, "moderate"),
        ("Maturity", 30, 20, 35, "low"),
    ],
    "Sugarcane": [
        ("Germination", 30, 20, 32, "high"),
        ("Tillering", 60, 20, 35, "high"),
        ("Grand Growth", 120, 25, 35, "high"),
        ("Maturation", 90, 20, 32, "moderate"),
    ],
    "Tomato": [
        ("Seedling", 30, 18, 28, "moderate"),
        ("Vegetative", 35, 18, 30, "moderate"),
        ("Flowering", 25, 20, 30, "high"),
        ("Fruit Development", 40, 18, 30, "high"),
        ("Maturity", 25, 18, 30, "moderate"),
    ],
    "Potato": [
        ("Sprouting", 20, 15, 25, "moderate"),
        ("Vegetative", 35, 15, 25, "moderate"),
        ("Tuber Formation", 30, 15, 23, "high"),
        ("Tuber Bulking", 40, 15, 25, "high"),
        ("Maturity", 20, 15, 25, "low"),
    ],
    "Chickpea": [
        ("Germination", 10, 15, 25, "moderate"),
        ("Vegetative", 35, 15, 28, "low"),
        ("Flowering", 25, 18, 30, "moderate"),
        ("Pod Development", 30, 18, 30, "moderate"),
        ("Maturity", 20, 18, 30, "low"),
    ],
}


STRESS_CONDITIONS = {
    "Wheat": [
        (
            "water_stress",
            "Low vegetation index, high temperature, low rainfall",
            "medium",
            "Check irrigation and inspect soil moisture.",
        ),
        (
            "heat_stress",
            "High temperature during flowering or grain filling",
            "high",
            "Monitor irrigation and crop condition closely.",
        ),
    ],
    "Rice": [
        (
            "water_stress",
            "Dry conditions or insufficient water during active growth",
            "high",
            "Check irrigation and water availability.",
        ),
    ],
    "Maize": [
        (
            "water_stress",
            "Low vegetation index combined with hot and dry conditions",
            "medium",
            "Inspect irrigation and soil moisture.",
        ),
        (
            "heat_stress",
            "High temperature during flowering",
            "high",
            "Monitor crop closely and maintain adequate water.",
        ),
    ],
    "Cotton": [
        (
            "water_stress",
            "Low vegetation index with dry conditions",
            "medium",
            "Inspect irrigation and soil moisture.",
        ),
    ],
    "Sugarcane": [
        (
            "water_stress",
            "Low vegetation index and prolonged dry conditions",
            "high",
            "Check irrigation and soil moisture immediately.",
        ),
    ],
    "Tomato": [
        (
            "water_stress",
            "Wilting indicators or low vegetation index under dry conditions",
            "medium",
            "Check irrigation and soil moisture.",
        ),
        (
            "heat_stress",
            "High temperature during flowering or fruit development",
            "high",
            "Monitor water availability and plant condition.",
        ),
    ],
    "Potato": [
        (
            "water_stress",
            "Low vegetation index and dry soil conditions",
            "medium",
            "Check irrigation and soil moisture.",
        ),
    ],
    "Chickpea": [
        (
            "water_stress",
            "Extended dry conditions during flowering",
            "medium",
            "Inspect soil moisture and water availability.",
        ),
    ],
}


SOILS = [
    (
        "Sandy Loam",
        "sandy loam",
        5.5,
        7.5,
        "low-moderate",
        "excellent",
        "Good drainage but relatively low water retention.",
    ),
    (
        "Loam",
        "loam",
        6.0,
        7.5,
        "moderate-high",
        "good",
        "Balanced agricultural soil with moderate water retention.",
    ),
    (
        "Clay Loam",
        "clay loam",
        6.0,
        7.5,
        "high",
        "moderate",
        "High water retention with slower drainage.",
    ),
    (
        "Clay",
        "clay",
        6.0,
        7.5,
        "very high",
        "poor-moderate",
        "High water retention but drainage can be limited.",
    ),
]


def seed_database() -> None:
    connection = get_connection()

    try:
        for crop in CROPS:
            connection.execute(
                """
                INSERT OR IGNORE INTO crops (
                    name,
                    scientific_name,
                    description,
                    min_temperature_c,
                    max_temperature_c,
                    min_rainfall_mm,
                    max_rainfall_mm,
                    min_ph,
                    max_ph,
                    water_requirement,
                    preferred_soil_texture,
                    water_retention,
                    drainage
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(crop.values()),
            )

        crop_ids = {}

        rows = connection.execute(
            "SELECT id, name FROM crops"
        ).fetchall()

        for row in rows:
            crop_ids[row["name"]] = row["id"]

        for crop_name, stages in GROWTH_STAGES.items():
            crop_id = crop_ids.get(crop_name)

            if not crop_id:
                continue

            for stage in stages:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO growth_stages (
                        crop_id,
                        stage_name,
                        duration_days,
                        min_temperature_c,
                        max_temperature_c,
                        water_requirement,
                        notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        crop_id,
                        stage[0],
                        stage[1],
                        stage[2],
                        stage[3],
                        stage[4],
                        None,
                    ),
                )

        for crop_name, stresses in STRESS_CONDITIONS.items():
            crop_id = crop_ids.get(crop_name)

            if not crop_id:
                continue

            for stress in stresses:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO stress_conditions (
                        crop_id,
                        condition_name,
                        indicators,
                        severity,
                        recommendation
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        crop_id,
                        stress[0],
                        stress[1],
                        stress[2],
                        stress[3],
                    ),
                )

        for soil in SOILS:
            connection.execute(
                """
                INSERT OR IGNORE INTO soil_profiles (
                    name,
                    texture,
                    ph_min,
                    ph_max,
                    water_retention,
                    drainage,
                    description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                soil,
            )

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    from .database import initialize_database

    initialize_database()
    seed_database()

    print("Agricultural knowledge base initialized successfully.")