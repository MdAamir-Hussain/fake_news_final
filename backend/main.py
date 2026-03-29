"""
FastAPI Backend — Fake News / Spam Detection API
"""

import json
import os
from pathlib import Path

import joblib
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from preprocessor import TextPreprocessor

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR  = Path(__file__).parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Fake News / Spam Detection API",
    description="ML-powered text classification. POST /predict to classify text.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Globals ──────────────────────────────────────────────────────────────────

preprocessor: TextPreprocessor = TextPreprocessor()
model = None
model_info: dict = {}


@app.on_event("startup")
async def load_model():
    global model, model_info
    model_path = MODEL_DIR / "best_model.joblib"
    info_path  = MODEL_DIR / "model_info.json"

    if not model_path.exists():
        print("[WARN] No model found at models/best_model.joblib")
        print("   Run:  python backend/model_trainer.py")
        return

    model = joblib.load(model_path)

    if info_path.exists():
        with open(info_path) as f:
            model_info = json.load(f)

    print(f"[OK] Model loaded: {model_info.get('model_name', 'unknown')}")
    print(f"     Accuracy: {model_info.get('accuracy', 'N/A')}")


# ── Schemas ──────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text must not be empty")
        if len(v) > 10_000:
            raise ValueError("text exceeds 10 000 character limit")
        return v.strip()


class ClassProbability(BaseModel):
    label: str
    probability: float


class PredictResponse(BaseModel):
    prediction: str          # e.g. "SPAM" or "HAM"
    label: int               # 0 or 1
    confidence: float        # probability of predicted class
    probabilities: dict      # {class_name: probability}
    processed_text: str      # what the model actually saw


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str
    model_name: str | None
    accuracy: float | None
    classes: list[str] | None


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Fake News / Spam Detection API",
        "docs": "/docs",
        "health": "/health",
        "predict": "POST /predict",
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    return HealthResponse(
        status="ready" if model is not None else "no_model",
        model_name=model_info.get("model_name"),
        accuracy=model_info.get("accuracy"),
        classes=model_info.get("classes"),
    )


@app.get("/model-info", tags=["info"])
async def get_model_info():
    if not model_info:
        raise HTTPException(status_code=404, detail="No model info available")
    return model_info


@app.post("/predict", response_model=PredictResponse, tags=["predict"])
async def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run model_trainer.py first.",
        )

    processed = preprocessor.preprocess(request.text)

    proba  = model.predict_proba([processed])[0]
    label  = int(np.argmax(proba))
    confidence = float(proba[label])

    classes = model_info.get("classes", ["ham", "spam"])

    # Build human-readable prediction label
    raw_class = classes[label]
    prediction = raw_class.upper()

    return PredictResponse(
        prediction=prediction,
        label=label,
        confidence=round(confidence, 4),
        probabilities={classes[i]: round(float(proba[i]), 4) for i in range(len(classes))},
        processed_text=processed,
    )
