# ============================================================
# Smart Agriculture Assistant
# Plant Disease Detection - Prediction
# ============================================================

# ------------------------------------------------------------
# Import required libraries
# ------------------------------------------------------------

import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras

# Import the same ResNet50 preprocessing function
# used when the disease models were trained.
from tensorflow.keras.applications.resnet50 import preprocess_input


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

PROJECT_ROOT = r"D:\projects\Smart_Agriculture_Assistant"

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "models",
    "disease"
)

ENCODER_DIR = os.path.join(
    PROJECT_ROOT,
    "models",
    "disease_label_encoders"
)


# ------------------------------------------------------------
# Image configuration
# ------------------------------------------------------------

IMAGE_SIZE = (224, 224)


# ------------------------------------------------------------
# Dataset-specific model and label encoder mapping
# ------------------------------------------------------------

DATASET_CONFIG = {

    "apple": {
        "model": "apple_resnet50_finetuned.keras",
        "encoder": "apple_label_encoder.pkl"
    },

    "black_gram_leaf": {
        "model": "black_gram_leaf_resnet50_finetuned.keras",
        "encoder": "Black_Gram_Leaf_label_encoder.pkl"
    },

    "coconut": {
        "model": "coconut_resnet50_finetuned.keras",
        "encoder": "Coconut_label_encoder.pkl"
    },

    "coffee": {
        "model": "coffee_resnet50_finetuned.keras",
        "encoder": "coffee_label_encoder.pkl"
    },

    "grapes": {
        "model": "grapes_resnet50_finetuned.keras",
        "encoder": "grapes_label_encoder.pkl"
    },

    "jute": {
        "model": "jute_resnet50_finetuned.keras",
        "encoder": "jute_label_encoder.pkl"
    },

    "maize": {
        "model": "maize_resnet50_finetuned.keras",
        "encoder": "maize_label_encoder.pkl"
    },

    "mango": {
        "model": "mango_resnet50_finetuned_best.keras",
        "encoder": "mango_label_encoder.pkl"
    },

    "orange": {
        "model": "orange_resnet50_finetuned.keras",
        "encoder": "orange_label_encoder.pkl"
    },

    "pigonpea": {
        "model": "pigonpea_resnet50_finetuned.keras",
        "encoder": "pigonpea_label_encoder.pkl"
    },

    "plant_wild": {
        "model": "plant_wild_resnet50_finetuned.keras",
        "encoder": "plant_wild_label_encoder.pkl"
    },

    "rice": {
        "model": "rice_resnet50_finetuned.keras",
        "encoder": "rice_label_encoder.pkl"
    },

    "watermelon": {
        "model": "watermelon_resnet50_finetuned.keras",
        "encoder": "Watermelon_label_encoder.pkl"
    }
}


# ------------------------------------------------------------
# Load image
# ------------------------------------------------------------

image_path = input(
    "\nEnter the path of the plant leaf image: "
).strip().strip('"')


# ------------------------------------------------------------
# Check image path
# ------------------------------------------------------------

if not os.path.isfile(image_path):

    print("\nError: Image file not found.")
    print("Please check the image path.")

    raise SystemExit


# ------------------------------------------------------------
# Display available datasets
# ------------------------------------------------------------

print("\nAvailable plant datasets:")

for dataset in DATASET_CONFIG:
    print(f" - {dataset}")


# ------------------------------------------------------------
# Select dataset
# ------------------------------------------------------------

dataset_name = input(
    "\nEnter the dataset/plant name: "
).strip().lower()


# ------------------------------------------------------------
# Validate dataset
# ------------------------------------------------------------

if dataset_name not in DATASET_CONFIG:

    print("\nError: Invalid dataset name.")

    raise SystemExit


# ------------------------------------------------------------
# Get model and encoder filenames
# ------------------------------------------------------------

model_path = os.path.join(
    MODEL_DIR,
    DATASET_CONFIG[dataset_name]["model"]
)

encoder_path = os.path.join(
    ENCODER_DIR,
    DATASET_CONFIG[dataset_name]["encoder"]
)


# ------------------------------------------------------------
# Check model and encoder
# ------------------------------------------------------------

if not os.path.isfile(model_path):

    print("\nError: Model file not found:")
    print(model_path)

    raise SystemExit


if not os.path.isfile(encoder_path):

    print("\nError: Label encoder not found:")
    print(encoder_path)

    raise SystemExit


# ------------------------------------------------------------
# Load trained ResNet50 model
# ------------------------------------------------------------

print("\nLoading ResNet50 model...")

model = keras.models.load_model(
    model_path,
    compile=False,
    safe_mode=False,
     custom_objects={
        "preprocess_input": preprocess_input
    }
)


# ------------------------------------------------------------
# Load dataset-specific label encoder
# ------------------------------------------------------------

print("Loading label encoder...")

with open(encoder_path, "rb") as file:

    label_encoder = pickle.load(file)


# ------------------------------------------------------------
# Load and preprocess image
# ------------------------------------------------------------

image = tf.keras.utils.load_img(
    image_path,
    target_size=IMAGE_SIZE
)

image = tf.keras.utils.img_to_array(image)

# Keep pixel values in the 0-255 range.
# The trained model already contains ResNet50 preprocessing.
image = image.astype(np.float32)

# Add batch dimension.
image = np.expand_dims(image, axis=0)


# ------------------------------------------------------------
# Make prediction
# ------------------------------------------------------------

print("Predicting disease...")

predictions = model.predict(
    image,
    verbose=0
)


# ------------------------------------------------------------
# Get predicted class
# ------------------------------------------------------------

predicted_index = np.argmax(
    predictions[0]
)


predicted_class = label_encoder.inverse_transform(
    [predicted_index]
)[0]


# ------------------------------------------------------------
# Get prediction confidence
# ------------------------------------------------------------

confidence = float(
    predictions[0][predicted_index]
) * 100


# ------------------------------------------------------------
# Display result
# ------------------------------------------------------------

print("\n" + "=" * 50)
print("        PLANT DISEASE PREDICTION")
print("=" * 50)

print(f"Plant/Dataset : {dataset_name}")
print(f"Prediction    : {predicted_class}")
print(f"Confidence    : {confidence:.2f}%")

print("=" * 50)