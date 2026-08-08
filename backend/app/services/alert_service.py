"""
Farm-level alert generation.

Creates alerts from the final cell status.
"""

def generate_alerts(cells):
    """
    Generate farm-level alerts from analyzed cells.
    """

    alerts = []

    for cell in cells:

        status = cell["status"]
        severity = cell["severity"]

        if status == "healthy":
            continue

        # ------------------------------------------
        # Dry / vegetation stress
        # ------------------------------------------

        if status == "dry":

            alerts.append(
                {
                    "cell": cell["id"],
                    "severity": severity,
                    "message": cell.get(
                        "issue",
                        "Vegetation stress detected.",
                    ),
                    "action": cell.get(
                        "recommended_action",
                        "Inspect the affected area.",
                    ),
                }
            )

        # ------------------------------------------
        # Disease
        # ------------------------------------------

        elif status == "disease":

            alerts.append(
                {
                    "cell": cell["id"],
                    "severity": severity,
                    "message": cell.get(
                        "issue",
                        "Possible disease detected.",
                    ),
                    "action": cell.get(
                        "recommended_action",
                        "Inspect affected plants.",
                    ),
                }
            )

        # ------------------------------------------
        # Pest
        # ------------------------------------------

        elif status == "pest":

            alerts.append(
                {
                    "cell": cell["id"],
                    "severity": severity,
                    "message": cell.get(
                        "issue",
                        "Possible pest activity detected.",
                    ),
                    "action": cell.get(
                        "recommended_action",
                        "Inspect affected plants.",
                    ),
                }
            )

    return alerts