"""Train and persist AgroAI crop recommendation model."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


RangeMap = Dict[str, Tuple[float, float]]


# Realistic agronomic ranges for 20 crops:
# N, P, K values are in kg/ha; pH is unitless; temperature in Celsius; humidity in %
CROP_RANGES: Dict[str, RangeMap] = {
    "Rice": {"N": (80, 100), "P": (40, 60), "K": (40, 60), "ph": (5.5, 7.0), "temperature": (20, 35), "humidity": (70, 90)},
    "Wheat": {"N": (80, 120), "P": (35, 60), "K": (30, 50), "ph": (6.0, 7.5), "temperature": (10, 25), "humidity": (45, 65)},
    "Maize": {"N": (70, 110), "P": (30, 60), "K": (25, 50), "ph": (5.8, 7.2), "temperature": (18, 32), "humidity": (50, 75)},
    "Chickpea": {"N": (15, 40), "P": (40, 70), "K": (30, 60), "ph": (6.0, 8.0), "temperature": (15, 30), "humidity": (35, 60)},
    "Lentil": {"N": (20, 45), "P": (35, 65), "K": (25, 55), "ph": (6.0, 7.8), "temperature": (12, 26), "humidity": (35, 60)},
    "Pomegranate": {"N": (30, 60), "P": (20, 45), "K": (35, 70), "ph": (5.5, 7.5), "temperature": (18, 34), "humidity": (40, 70)},
    "Banana": {"N": (90, 130), "P": (50, 80), "K": (120, 180), "ph": (5.5, 7.0), "temperature": (24, 35), "humidity": (65, 90)},
    "Mango": {"N": (40, 70), "P": (25, 50), "K": (40, 80), "ph": (5.5, 7.5), "temperature": (24, 38), "humidity": (45, 75)},
    "Grapes": {"N": (45, 75), "P": (30, 60), "K": (60, 120), "ph": (5.5, 7.0), "temperature": (15, 30), "humidity": (40, 65)},
    "Watermelon": {"N": (60, 95), "P": (30, 55), "K": (60, 105), "ph": (6.0, 7.5), "temperature": (22, 35), "humidity": (50, 75)},
    "Muskmelon": {"N": (55, 90), "P": (30, 55), "K": (65, 110), "ph": (6.0, 7.5), "temperature": (22, 34), "humidity": (50, 75)},
    "Apple": {"N": (20, 40), "P": (100, 130), "K": (100, 140), "ph": (5.5, 6.5), "temperature": (10, 22), "humidity": (40, 60)},
    "Orange": {"N": (55, 85), "P": (25, 50), "K": (55, 95), "ph": (5.5, 7.0), "temperature": (18, 32), "humidity": (45, 70)},
    "Papaya": {"N": (80, 120), "P": (40, 70), "K": (110, 170), "ph": (5.5, 7.0), "temperature": (22, 35), "humidity": (60, 85)},
    "Coconut": {"N": (50, 90), "P": (20, 45), "K": (90, 160), "ph": (5.2, 7.8), "temperature": (24, 34), "humidity": (65, 90)},
    "Cotton": {"N": (70, 120), "P": (30, 55), "K": (40, 80), "ph": (5.5, 8.0), "temperature": (20, 35), "humidity": (40, 70)},
    "Jute": {"N": (75, 115), "P": (30, 55), "K": (35, 70), "ph": (5.0, 7.5), "temperature": (24, 35), "humidity": (70, 90)},
    "Coffee": {"N": (60, 95), "P": (25, 50), "K": (60, 100), "ph": (5.0, 6.5), "temperature": (15, 28), "humidity": (55, 80)},
    "Tea": {"N": (70, 110), "P": (25, 45), "K": (65, 110), "ph": (4.5, 6.0), "temperature": (13, 28), "humidity": (65, 90)},
    "Mustard": {"N": (45, 80), "P": (20, 45), "K": (25, 55), "ph": (6.0, 8.0), "temperature": (10, 25), "humidity": (35, 60)},
}


def generate_synthetic_dataset(samples_per_crop: int = 110) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic training data for all crops."""
    np.random.seed(42)

    features: list[list[float]] = []
    labels: list[str] = []

    for crop, ranges in CROP_RANGES.items():
        # Compute crop-specific centers and sample around them with bounded variance.
        centers = {key: (low + high) / 2 for key, (low, high) in ranges.items()}
        for _ in range(samples_per_crop):
            # Sample mostly near the crop center while respecting min/max ranges.
            n = np.random.normal(centers["N"], (ranges["N"][1] - ranges["N"][0]) / 6)
            p = np.random.normal(centers["P"], (ranges["P"][1] - ranges["P"][0]) / 6)
            k = np.random.normal(centers["K"], (ranges["K"][1] - ranges["K"][0]) / 6)
            ph = np.random.normal(centers["ph"], (ranges["ph"][1] - ranges["ph"][0]) / 7)
            temperature = np.random.normal(
                centers["temperature"],
                (ranges["temperature"][1] - ranges["temperature"][0]) / 7,
            )
            humidity = np.random.normal(
                centers["humidity"],
                (ranges["humidity"][1] - ranges["humidity"][0]) / 7,
            )

            feature_row = [
                float(np.clip(n, *ranges["N"])),
                float(np.clip(p, *ranges["P"])),
                float(np.clip(k, *ranges["K"])),
                float(np.clip(ph, *ranges["ph"])),
                float(np.clip(temperature, *ranges["temperature"])),
                float(np.clip(humidity, *ranges["humidity"])),
            ]

            features.append(feature_row)
            labels.append(crop)

    return np.array(features, dtype=np.float32), np.array(labels)


def main() -> None:
    """Train RandomForest model, print metrics, and save artifacts."""
    print("Generating synthetic dataset...")
    x, y = generate_synthetic_dataset(samples_per_crop=110)  # ~2200 samples total
    print(f"Dataset size: {x.shape[0]} samples, {x.shape[1]} features")

    # Encode crop names to numeric classes for scikit-learn.
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Stratified split preserves class balance in train/test sets.
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=15,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)

    print("\n=== Classification Report ===")
    print(report)
    print(f"Accuracy: {accuracy * 100:.2f}%")

    # Persist artifacts under agro-api/model/.
    script_dir = Path(__file__).resolve().parent
    model_dir = script_dir.parent / "model"
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "crop_model.pkl"
    encoder_path = model_dir / "label_encoder.pkl"
    joblib.dump(model, model_path)
    joblib.dump(label_encoder, encoder_path)

    print(f"Saved model to: {model_path}")
    print(f"Saved label encoder to: {encoder_path}")


if __name__ == "__main__":
    main()

