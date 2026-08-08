"""
Grid analysis service.

Splits an image into exactly 16 cells (4x4)
and independently analyzes each cell.
"""

from app.services.analysis_service import (
    calculate_exg,
    summarize_exg,
)

from app.services.classification_service import (
    classify_health,
)

from app.services.recommendation_service import (
    generate_recommendation,
)


GRID_ROWS = 4
GRID_COLS = 4


def split_into_grid(
    image,
    rows: int = GRID_ROWS,
    cols: int = GRID_COLS,
):
    """
    Split an image into a fixed 4x4 grid.

    Returns exactly 16 cells.
    """

    if rows <= 0 or cols <= 0:
        raise ValueError(
            "Grid rows and columns must be positive."
        )

    height, width = image.shape[:2]

    if height < rows or width < cols:
        raise ValueError(
            "Image is too small for the requested grid."
        )

    cell_height = height // rows
    cell_width = width // cols

    cells = []

    for row in range(rows):

        for col in range(cols):

            y_start = row * cell_height

            # Last row gets the remaining pixels.
            y_end = (
                height
                if row == rows - 1
                else (row + 1) * cell_height
            )

            x_start = col * cell_width

            # Last column gets the remaining pixels.
            x_end = (
                width
                if col == cols - 1
                else (col + 1) * cell_width
            )

            cropped = image[
                y_start:y_end,
                x_start:x_end,
            ]

            cell_id = (
                f"{chr(65 + row)}{col + 1}"
            )

            cells.append(
                {
                    "id": cell_id,
                    "row": row + 1,
                    "col": col + 1,
                    "image": cropped,
                }
            )

    if len(cells) != rows * cols:
        raise RuntimeError(
            "Grid generation failed."
        )

    return cells


def analyze_grid(cells):
    """
    Analyze every grid cell independently.
    """

    analyzed_cells = []

    for cell in cells:

        exg = calculate_exg(
            cell["image"]
        )

        summary = summarize_exg(exg)

        classification = classify_health(
            summary["average"]
        )

        recommendation = (
            generate_recommendation(
                classification,
                exg_value=summary["average"],
            )
        )

        analyzed_cells.append(
            {
                "id": cell["id"],
                "row": cell["row"],
                "col": cell["col"],

                "status": recommendation[
                    "status"
                ],

                "severity": recommendation[
                    "severity"
                ],

                "confidence": recommendation[
                    "confidence"
                ],

                "issue": recommendation[
                    "issue"
                ],

                "recommended_action": (
                    recommendation[
                        "recommended_action"
                    ]
                ),

                "exg_value": round(
                    summary["average"],
                    2,
                ),
            }
        )

    if len(analyzed_cells) != 16:
        raise RuntimeError(
            f"Expected 16 cells, got "
            f"{len(analyzed_cells)}."
        )

    return analyzed_cells