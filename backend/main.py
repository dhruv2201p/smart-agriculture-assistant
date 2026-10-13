"""
Smart Agriculture Assistant - FastAPI Backend Entrypoint
Provides endpoints for:
- Health checks: GET /health
- Crop Recommendation: POST /api/crop/predict
- Disease Detection: POST /api/disease/predict
- Agriculture Chatbot: POST /api/chat
"""

import os
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

from crop import predict_crop
from disease import predict_disease, get_supported_crops, get_disease_health
from chatbot import get_chat_response

app = FastAPI(
    title="Smart Agriculture Assistant API",
    description="Backend API for crop recommendation, leaf disease detection, and agriculture chatbot.",
    version="1.0.0"
)

# -------------------------------------------------------------
# CORS Configuration (Configurable via CORS_ORIGINS env var)
# -------------------------------------------------------------
raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
if "*" in origins:
    allow_origins = ["*"]
else:
    allow_origins = origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Pydantic Request Schemas
# -------------------------------------------------------------
class CropRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, le=500, description="Nitrogen content (kg/ha)")
    phosphorus: float = Field(..., ge=0, le=500, description="Phosphorus content (kg/ha)")
    potassium: float = Field(..., ge=0, le=500, description="Potassium content (kg/ha)")
    temperature: float = Field(..., ge=-20, le=65, description="Temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    ph: float = Field(..., ge=1, le=14, description="Soil pH value")
    rainfall: float = Field(..., ge=0, le=3000, description="Rainfall (mm)")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Farmer user message")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Session chat history")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Active crop or disease context")


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------
@app.get("/")
def root():
    """Root endpoint for Render default health checks and quick status."""
    return {
        "status": "ok",
        "service": "Smart Agriculture Assistant API",
        "health": "/health",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Service health check including disease subsystem state."""
    return {
        "status": "ok",
        "service": "Smart Agriculture Assistant API",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "disease_module": get_disease_health()
    }


@app.get("/api/disease/health")
def disease_health_endpoint():
    """Dedicated diagnostic health check for plant disease detection subsystem."""
    return {"status": "ok", "data": get_disease_health()}


@app.post("/api/crop/predict")
def predict_crop_endpoint(payload: CropRequest):
    """
    Predict optimal crop based on soil and weather parameters.
    """
    try:
        result = predict_crop(
            nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus,
            potassium=payload.potassium,
            temperature=payload.temperature,
            humidity=payload.humidity,
            ph=payload.ph,
            rainfall=payload.rainfall
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crop prediction failed: {str(e)}")


@app.get("/api/disease/crops")
def get_supported_crops_endpoint():
    """List of 13 supported plants for leaf disease diagnosis."""
    return {"crops": get_supported_crops()}


@app.post("/api/disease/predict")
async def predict_disease_endpoint(
    file: UploadFile = File(..., description="Leaf image file"),
    crop_name: str = Form(..., description="Crop identifier, e.g. 'apple'")
):
    """
    Predict plant disease from uploaded leaf image and crop name.
    Includes upload validation, top-3 candidates, and treatment advice.
    """
    # 1. Validate content type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type and file.content_type.lower() not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image format '{file.content_type}'. Please upload a JPG, PNG, or WEBP photo."
        )

    try:
        image_bytes = await file.read()
        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded image is empty (0 bytes). Please select a valid photo.")

        result = predict_disease(image_bytes=image_bytes, crop_key=crop_name)
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except ValueError as ve:
        # User input or validation error
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        # Model file not found on disk or failed download
        raise HTTPException(
            status_code=503,
            detail=f"The deep learning model weights for '{crop_name}' are currently unavailable. Please try again shortly."
        )
    except Exception as e:
        # Log internal error and return sanitized message
        import logging
        logging.getLogger("uvicorn.error").error(f"Disease prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the leaf image. Please ensure the image is clear and try again."
        )


@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest):
    """
    Send farming question to Gemini chatbot with history and active context.
    """
    try:
        formatted_history = [
            {"role": msg.role, "content": msg.content} for msg in payload.history
        ]
        reply = get_chat_response(
            message=payload.message,
            history=formatted_history,
            context=payload.context
        )
        return {"success": True, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
