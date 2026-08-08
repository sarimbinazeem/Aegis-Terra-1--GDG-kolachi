from typing import Optional

from .database import get_connection


def list_crops() -> list[dict]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                scientific_name,
                description
            FROM crops
            ORDER BY name
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_crop(name: str) -> Optional[dict]:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM crops
            WHERE LOWER(name) = LOWER(?)
            """,
            (name.strip(),),
        ).fetchone()

        if row is None:
            return None

        crop = dict(row)

        crop["growth_stages"] = [
            dict(stage)
            for stage in connection.execute(
                """
                SELECT *
                FROM growth_stages
                WHERE crop_id = ?
                ORDER BY id
                """,
                (crop["id"],),
            ).fetchall()
        ]

        crop["stress_conditions"] = [
            dict(stress)
            for stress in connection.execute(
                """
                SELECT *
                FROM stress_conditions
                WHERE crop_id = ?
                ORDER BY id
                """,
                (crop["id"],),
            ).fetchall()
        ]

        return crop

    finally:
        connection.close()


def list_soils() -> list[dict]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM soil_profiles
            ORDER BY name
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_soil(name: str) -> Optional[dict]:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM soil_profiles
            WHERE LOWER(name) = LOWER(?)
            """,
            (name.strip(),),
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()