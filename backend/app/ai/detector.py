"""
Aegis-Terra YOLO Detection Layer

IMPORTANT:
This module provides generic visual object detection.

The default YOLO model is NOT a crop-disease classifier.
Therefore detections from the default model must never be
interpreted as "disease detected" or "pest detected" unless
a crop-specific trained model is supplied.

Pipeline responsibility:

    Image
      ↓
    YOLO object detection
      ↓
    Generic visual detections
      ↓
    Combined with ExG crop-health analysis elsewhere

The detector is deliberately isolated from crop-health
classification so the system remains scientifically honest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ultralytics import YOLO


# ============================================================
# Configuration
# ============================================================

# Expected location for a future crop-specific model.
#
# Example:
#
# backend/app/ai/models/crop_detector.pt

MODEL_DIR = Path(__file__).resolve().parent / "models"

GENERIC_MODEL_PATH = MODEL_DIR / "yolov8n.pt"

# A crop-specific model can later be placed here.
CROP_MODEL_PATH = MODEL_DIR / "crop_detector.pt"

DEFAULT_CONFIDENCE = 0.25


# ============================================================
# Detector
# ============================================================

class CropDetector:
    """
    YOLO detection wrapper.

    If crop_detector.pt exists:
        use the crop-specific model.

    Otherwise:
        use yolov8n.pt as a generic visual detector.

    The return format remains stable in both cases.
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        confidence: float = DEFAULT_CONFIDENCE,
    ) -> None:

        MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.confidence = confidence

        # ----------------------------------------------------
        # Model selection
        # ----------------------------------------------------

        if model_path is not None:

            selected_path = Path(
                model_path
            )

        elif CROP_MODEL_PATH.exists():

            selected_path = CROP_MODEL_PATH

        else:

            selected_path = GENERIC_MODEL_PATH

        self.model_path = selected_path

        # ----------------------------------------------------
        # Load model
        # ----------------------------------------------------

        if not self.model_path.exists():

            # Ultralytics may automatically download the
            # generic model when given the model filename.
            #
            # This is intentionally only the generic fallback.

            self.model = YOLO(
                str(self.model_path)
            )

        else:

            self.model = YOLO(
                str(self.model_path)
            )

        self.is_crop_specific = (
            self.model_path.name
            == CROP_MODEL_PATH.name
        )

    # ========================================================
    # Detection
    # ========================================================

    def detect(
        self,
        image_path: str | Path,
        confidence: float | None = None,
    ) -> list[dict[str, Any]]:

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        conf = (
            confidence
            if confidence is not None
            else self.confidence
        )

        results = self.model.predict(
            source=str(image_path),
            conf=conf,
            verbose=False,
        )

        detections: list[dict[str, Any]] = []

        for result in results:

            boxes = getattr(
                result,
                "boxes",
                None,
            )

            if boxes is None:
                continue

            names = getattr(
                result,
                "names",
                {},
            )

            for box in boxes:

                class_id = int(
                    box.cls[0].item()
                )

                confidence_value = float(
                    box.conf[0].item()
                )

                coordinates = (
                    box.xyxy[0]
                    .tolist()
                )

                class_name = str(
                    names.get(
                        class_id,
                        class_id,
                    )
                )

                detections.append(
                    {
                        "class_id": class_id,
                        "class": class_name,
                        "confidence": round(
                            confidence_value,
                            4,
                        ),
                        "bbox": [
                            round(
                                float(value),
                                2,
                            )
                            for value in coordinates
                        ],
                        "source": (
                            "crop_specific_yolo"
                            if self.is_crop_specific
                            else "generic_yolo"
                        ),
                    }
                )

        return detections

    # ========================================================
    # Model information
    # ========================================================

    def model_info(
        self,
    ) -> dict[str, Any]:

        return {
            "model": self.model_path.name,
            "model_type": (
                "crop_specific"
                if self.is_crop_specific
                else "generic"
            ),
            "crop_disease_detection": (
                self.is_crop_specific
            ),
        }


# ============================================================
# Singleton detector
# ============================================================

_detector: CropDetector | None = None


def get_detector() -> CropDetector:

    global _detector

    if _detector is None:

        _detector = CropDetector()

    return _detector


# ============================================================
# Public helper
# ============================================================

def detect_objects(
    image_path: str | Path,
    confidence: float = DEFAULT_CONFIDENCE,
) -> list[dict[str, Any]]:

    detector = get_detector()

    return detector.detect(
        image_path=image_path,
        confidence=confidence,
    )


def get_detector_info() -> dict[str, Any]:

    return get_detector().model_info()
