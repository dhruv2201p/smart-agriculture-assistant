"""
Plant Disease Detection Service
Features:
- Lazy loading of ResNet50 models per crop
- Single-model memory caching to support low-memory hosting (Render 512MB RAM)
- Automatic model download from Hugging Face Hub or cloud URL if missing locally
- Input validation for uploaded leaf images
"""

import os
import gc
import pickle
import urllib.request
from io import BytesIO
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image

# Disable noisy TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.resnet50 import preprocess_input

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "disease")
ENCODER_DIR = os.path.join(BASE_DIR, "models", "disease_label_encoders")
IMAGE_SIZE = (224, 224)
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit

DATASET_CONFIG = {
    "apple": {
        "model": "apple_resnet50_finetuned.keras",
        "encoder": "apple_label_encoder.pkl",
        "name": "Apple"
    },
    "black_gram_leaf": {
        "model": "black_gram_leaf_resnet50_finetuned.keras",
        "encoder": "Black_Gram_Leaf_label_encoder.pkl",
        "name": "Black Gram"
    },
    "coconut": {
        "model": "coconut_resnet50_finetuned.keras",
        "encoder": "Coconut_label_encoder.pkl",
        "name": "Coconut"
    },
    "coffee": {
        "model": "coffee_resnet50_finetuned.keras",
        "encoder": "coffee_label_encoder.pkl",
        "name": "Coffee"
    },
    "grapes": {
        "model": "grapes_resnet50_finetuned.keras",
        "encoder": "grapes_label_encoder.pkl",
        "name": "Grapes"
    },
    "jute": {
        "model": "jute_resnet50_finetuned.keras",
        "encoder": "jute_label_encoder.pkl",
        "name": "Jute"
    },
    "maize": {
        "model": "maize_resnet50_finetuned.keras",
        "encoder": "maize_label_encoder.pkl",
        "name": "Maize"
    },
    "mango": {
        "model": "mango_resnet50_finetuned_best.keras",
        "encoder": "mango_label_encoder.pkl",
        "name": "Mango"
    },
    "orange": {
        "model": "orange_resnet50_finetuned.keras",
        "encoder": "orange_label_encoder.pkl",
        "name": "Orange"
    },
    "pigonpea": {
        "model": "pigonpea_resnet50_finetuned.keras",
        "encoder": "pigonpea_label_encoder.pkl",
        "name": "Pigeon Pea"
    },
    "plant_wild": {
        "model": "plant_wild_resnet50_finetuned.keras",
        "encoder": "plant_wild_label_encoder.pkl",
        "name": "Wild Plant"
    },
    "rice": {
        "model": "rice_resnet50_finetuned.keras",
        "encoder": "rice_label_encoder.pkl",
        "name": "Rice"
    },
    "watermelon": {
        "model": "watermelon_resnet50_finetuned.keras",
        "encoder": "Watermelon_label_encoder.pkl",
        "name": "Watermelon"
    }
}

# Cache holds only the active crop model to avoid memory limits
_current_crop = None
_current_model = None
_current_encoder = None


def get_supported_crops() -> list:
    """Return list of supported crops with display names."""
    return [{"key": k, "name": v["name"]} for k, v in DATASET_CONFIG.items()]


def download_model_if_missing(model_filename: str, target_path: str):
    """
    Download .keras model file on demand from Hugging Face Hub or MODEL_BASE_URL
    if it is not present on disk.
    """
    if os.path.isfile(target_path):
        return target_path

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    hf_repo = os.getenv("HF_REPO_ID")
    base_url = os.getenv("MODEL_BASE_URL")

    # Option 1: Hugging Face Hub
    if hf_repo:
        try:
            from huggingface_hub import hf_hub_download
            print(f"Downloading {model_filename} from Hugging Face repo {hf_repo}...")
            downloaded = hf_hub_download(
                repo_id=hf_repo,
                filename=f"disease/{model_filename}",
                local_dir=os.path.join(BASE_DIR, "models")
            )
            return downloaded
        except Exception as e:
            print(f"Hugging Face download failed: {e}")

    # Option 2: Direct public URL
    if base_url:
        try:
            download_url = f"{base_url.rstrip('/')}/{model_filename}"
            print(f"Downloading {model_filename} from {download_url}...")
            urllib.request.urlretrieve(download_url, target_path)
            return target_path
        except Exception as e:
            print(f"Direct URL download failed: {e}")

    raise FileNotFoundError(
        f"Model file '{model_filename}' not found locally at {target_path}. "
        "Please provide local models or configure HF_REPO_ID or MODEL_BASE_URL in your environment."
    )


def load_crop_disease_model(crop_key: str):
    """
    Lazy-load requested crop model and label encoder.
    Evicts previously loaded model to preserve low-memory footprint.
    """
    global _current_crop, _current_model, _current_encoder

    crop_key = crop_key.lower().strip()
    if crop_key not in DATASET_CONFIG:
        raise ValueError(f"Unsupported crop '{crop_key}'. Supported crops: {list(DATASET_CONFIG.keys())}")

    # Return cached model if already loaded
    if _current_crop == crop_key and _current_model is not None:
        return _current_model, _current_encoder

    # Evict old model from GPU/RAM to stay within Render 512MB RAM limit
    if _current_model is not None:
        del _current_model
        del _current_encoder
        keras.backend.clear_session()
        gc.collect()

    config = DATASET_CONFIG[crop_key]
    model_path = os.path.join(MODEL_DIR, config["model"])
    encoder_path = os.path.join(ENCODER_DIR, config["encoder"])

    # Ensure model exists locally or download on demand
    model_path = download_model_if_missing(config["model"], model_path)

    if not os.path.isfile(encoder_path):
        raise FileNotFoundError(f"Label encoder not found: {encoder_path}")

    # Load trained model and encoder
    _current_model = keras.models.load_model(
        model_path,
        compile=False,
        safe_mode=False,
        custom_objects={"preprocess_input": preprocess_input}
    )

    with open(encoder_path, "rb") as f:
        _current_encoder = pickle.load(f)

    _current_crop = crop_key
    return _current_model, _current_encoder


def predict_disease(image_bytes: bytes, crop_key: str) -> dict:
    """
    Process leaf image and return predicted disease and confidence.
    """
    # Validate file size
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("Image file exceeds the 10 MB size limit.")

    # Validate image format
    try:
        pil_img = Image.open(BytesIO(image_bytes))
        pil_img.verify()
        pil_img = Image.open(BytesIO(image_bytes))  # Reopen after verify
    except Exception:
        raise ValueError("Invalid image file. Please upload a valid JPG, PNG, or WEBP image.")

    # Load model lazily
    model, encoder = load_crop_disease_model(crop_key)

    # Preprocess image
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    pil_img = pil_img.resize(IMAGE_SIZE)

    img_array = np.array(pil_img, dtype=np.float32)
    img_batch = np.expand_dims(img_array, axis=0)

    # Inference
    predictions = model.predict(img_batch, verbose=0)
    pred_idx = int(np.argmax(predictions[0]))
    predicted_class = encoder.inverse_transform([pred_idx])[0]
    confidence = float(predictions[0][pred_idx]) * 100.0

    is_healthy = "healthy" in predicted_class.lower()

    return {
        "plant": DATASET_CONFIG[crop_key]["name"],
        "crop_key": crop_key,
        "disease": str(predicted_class),
        "confidence": round(confidence, 2),
        "is_healthy": is_healthy
    }
