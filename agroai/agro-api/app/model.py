"""Model loading and prediction utilities for AgroAI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from app.schemas import SoilInput

logger = logging.getLogger(__name__)


class ModelManager:
    """Manage lazy loading of model artifacts and expose prediction API."""

    def __init__(self) -> None:
        """Initialize manager without loading model artifacts immediately."""
        self._model: Optional[RandomForestClassifier] = None
        self._label_encoder: Optional[LabelEncoder] = None
        self._model_path = Path(__file__).resolve().parent.parent / "model" / "crop_model.pkl"
        self._encoder_path = Path(__file__).resolve().parent.parent / "model" / "label_encoder.pkl"
        self._default_temperature = 25.0
        self._default_humidity = 65.0

    def load(self) -> None:
        """Load model artifacts from disk if not already loaded."""
        if self._model is not None and self._label_encoder is not None:
            logger.debug("Model artifacts already loaded.")
            return

        logger.info("Loading model artifacts from %s", self._model_path.parent)
        if not self._model_path.exists() or not self._encoder_path.exists():
            message = (
                "Model artifacts not found. Expected files: "
                f"{self._model_path} and {self._encoder_path}. "
                "Run 'python scripts/train_model.py' from agro-api/ first."
            )
            logger.error(message)
            raise RuntimeError(message)

        try:
            self._model = joblib.load(self._model_path)
            self._label_encoder = joblib.load(self._encoder_path)
            logger.info("Model artifacts loaded successfully.")
        except Exception as exc:  # pragma: no cover - defensive logging path
            message = f"Failed to load model artifacts: {exc}"
            logger.exception(message)
            raise RuntimeError(message) from exc

    def is_loaded(self) -> bool:
        """Return whether both model and encoder are loaded in memory."""
        return self._model is not None and self._label_encoder is not None

    def predict(self, soil_input: SoilInput) -> Dict[str, Any]:
        """
        Predict crop recommendation from validated soil input.

        Feature order must remain: [N, P, K, pH, temperature, humidity].
        """
        if not self.is_loaded():
            logger.debug("Lazy-loading model artifacts on first prediction.")
            self.load()

        assert self._model is not None  # For type narrowing after load().
        assert self._label_encoder is not None

        temperature = (
            soil_input.temperature
            if soil_input.temperature is not None
            else self._default_temperature
        )
        humidity = (
            soil_input.humidity if soil_input.humidity is not None else self._default_humidity
        )

        features = np.array(
            [[soil_input.N, soil_input.P, soil_input.K, soil_input.ph, temperature, humidity]],
            dtype=float,
        )
        logger.info(
            "Running crop prediction with features [N, P, K, pH, temp, humidity]=%s",
            features.tolist()[0],
        )

        probabilities = self._model.predict_proba(features)[0]
        winner_index = int(np.argmax(probabilities))
        confidence = float(probabilities[winner_index])
        crop = str(self._label_encoder.inverse_transform([winner_index])[0])

        # Select top 3 alternatives excluding the winner class.
        sorted_indices = np.argsort(probabilities)[::-1]
        alternative_indices: List[int] = [
            int(idx) for idx in sorted_indices if int(idx) != winner_index
        ][:3]
        alternatives = [
            str(self._label_encoder.inverse_transform([idx])[0]) for idx in alternative_indices
        ]

        result = {"crop": crop, "confidence": confidence, "alternatives": alternatives}
        logger.info("Prediction complete: %s", result)
        return result


# Singleton instance used across the API app.
model_manager = ModelManager()

