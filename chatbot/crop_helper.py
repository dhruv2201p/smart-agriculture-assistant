"""
Smart Agriculture Assistant - Crop Recommendation Helper
Safely loads pre-trained CatBoost model & scaler to provide crop recommendations and confidence.
"""

import os
import pickle
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "crop_model.pkl")
SCALER_PATH = os.path.join(PROJECT_ROOT, "models", "crop_scaler.pkl")

_CROP_MODEL = None
_CROP_SCALER = None


def _load_crop_artifacts():
    global _CROP_MODEL, _CROP_SCALER
    if _CROP_MODEL is None or _CROP_SCALER is None:
        with open(MODEL_PATH, "rb") as f:
            _CROP_MODEL = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            _CROP_SCALER = pickle.load(f)
    return _CROP_MODEL, _CROP_SCALER


def predict_crop_recommendation(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float
) -> Tuple[str, float]:
    """
    Predict optimal crop and model confidence based on soil and weather metrics.
    :return: (crop_name, confidence_percentage)
    """
    model, scaler = _load_crop_artifacts()

    input_df = pd.DataFrame([[
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        ph,
        rainfall
    ]], columns=[
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall"
    ])

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
    crop_name = str(np.asarray(prediction).ravel()[0])

    # Calculate prediction confidence if supported
    confidence = 0.0
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_scaled)
        confidence = float(np.max(probabilities)) * 100.0

    return crop_name, confidence
