"""
Smart Agriculture Assistant - Plant Disease Prediction Helper
Safely loads pre-trained ResNet50 models for UI inference without triggering CLI input prompts.
"""

import os
import pickle
from io import BytesIO
from typing import Dict, Tuple, Any, Optional
import numpy as np
from PIL import Image

# Suppress excessive TensorFlow logs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.resnet50 import preprocess_input

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(PROJECT_ROOT, "models", "disease")
ENCODER_DIR = os.path.join(PROJECT_ROOT, "models", "disease_label_encoders")
IMAGE_SIZE = (224, 224)

DATASET_CONFIG = {
    "apple": {
        "model": "apple_resnet50_finetuned.keras",
        "encoder": "apple_label_encoder.pkl",
        "display_name": "Apple"
    },
    "black_gram_leaf": {
        "model": "black_gram_leaf_resnet50_finetuned.keras",
        "encoder": "Black_Gram_Leaf_label_encoder.pkl",
        "display_name": "Black Gram"
    },
    "coconut": {
        "model": "coconut_resnet50_finetuned.keras",
        "encoder": "Coconut_label_encoder.pkl",
        "display_name": "Coconut"
    },
    "coffee": {
        "model": "coffee_resnet50_finetuned.keras",
        "encoder": "coffee_label_encoder.pkl",
        "display_name": "Coffee"
    },
    "grapes": {
        "model": "grapes_resnet50_finetuned.keras",
        "encoder": "grapes_label_encoder.pkl",
        "display_name": "Grapes"
    },
    "jute": {
        "model": "jute_resnet50_finetuned.keras",
        "encoder": "jute_label_encoder.pkl",
        "display_name": "Jute"
    },
    "maize": {
        "model": "maize_resnet50_finetuned.keras",
        "encoder": "maize_label_encoder.pkl",
        "display_name": "Maize"
    },
    "mango": {
        "model": "mango_resnet50_finetuned_best.keras",
        "encoder": "mango_label_encoder.pkl",
        "display_name": "Mango"
    },
    "orange": {
        "model": "orange_resnet50_finetuned.keras",
        "encoder": "orange_label_encoder.pkl",
        "display_name": "Orange"
    },
    "pigonpea": {
        "model": "pigonpea_resnet50_finetuned.keras",
        "encoder": "pigonpea_label_encoder.pkl",
        "display_name": "Pigeon Pea"
    },
    "plant_wild": {
        "model": "plant_wild_resnet50_finetuned.keras",
        "encoder": "plant_wild_label_encoder.pkl",
        "display_name": "Wild Plant"
    },
    "rice": {
        "model": "rice_resnet50_finetuned.keras",
        "encoder": "rice_label_encoder.pkl",
        "display_name": "Rice"
    },
    "watermelon": {
        "model": "watermelon_resnet50_finetuned.keras",
        "encoder": "Watermelon_label_encoder.pkl",
        "display_name": "Watermelon"
    }
}

# In-memory cache for loaded models and encoders
_LOADED_MODELS: Dict[str, Any] = {}
_LOADED_ENCODERS: Dict[str, Any] = {}


def get_available_plants() -> Dict[str, str]:
    """Returns mapping of dataset key to friendly display name."""
    return {k: v["display_name"] for k, v in DATASET_CONFIG.items()}


def load_disease_model(dataset_name: str):
    """Load and cache the trained ResNet50 model and encoder for a given plant."""
    dataset_name = dataset_name.lower().strip()
    if dataset_name not in DATASET_CONFIG:
        raise ValueError(f"Unknown plant dataset: {dataset_name}. Available: {list(DATASET_CONFIG.keys())}")

    if dataset_name in _LOADED_MODELS and dataset_name in _LOADED_ENCODERS:
        return _LOADED_MODELS[dataset_name], _LOADED_ENCODERS[dataset_name]

    model_path = os.path.join(MODEL_DIR, DATASET_CONFIG[dataset_name]["model"])
    encoder_path = os.path.join(ENCODER_DIR, DATASET_CONFIG[dataset_name]["encoder"])

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not os.path.isfile(encoder_path):
        raise FileNotFoundError(f"Label encoder file not found: {encoder_path}")

    model = keras.models.load_model(
        model_path,
        compile=False,
        safe_mode=False,
        custom_objects={"preprocess_input": preprocess_input}
    )

    with open(encoder_path, "rb") as f:
        encoder = pickle.load(f)

    _LOADED_MODELS[dataset_name] = model
    _LOADED_ENCODERS[dataset_name] = encoder

    return model, encoder


def predict_disease(
    image_input: Any,
    dataset_name: str
) -> Tuple[str, float]:
    """
    Predict plant disease from an image.
    :param image_input: File path (str), BytesIO, or PIL Image.
    :param dataset_name: Plant name key (e.g., 'apple', 'rice', 'maize').
    :return: (predicted_class_name, confidence_percentage)
    """
    model, encoder = load_disease_model(dataset_name)

    # Convert input to PIL Image
    if isinstance(image_input, str):
        pil_img = Image.open(image_input)
    elif isinstance(image_input, (bytes, bytearray)):
        pil_img = Image.open(BytesIO(image_input))
    elif hasattr(image_input, "read"):
        # UploadedFile or file-like
        image_input.seek(0)
        pil_img = Image.open(image_input)
    elif isinstance(image_input, Image.Image):
        pil_img = image_input
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Ensure RGB
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    # Resize to model input dimensions
    pil_img = pil_img.resize(IMAGE_SIZE)

    # Convert to numpy array float32 (0-255)
    img_array = np.array(pil_img, dtype=np.float32)
    img_batch = np.expand_dims(img_array, axis=0)

    # Model inference
    predictions = model.predict(img_batch, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))
    predicted_class = encoder.inverse_transform([predicted_index])[0]
    confidence = float(predictions[0][predicted_index]) * 100.0

    return str(predicted_class), float(confidence)
