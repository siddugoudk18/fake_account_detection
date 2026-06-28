"""
main.py — FastAPI Application for CADENCE-Spam
================================================
CADENCE-Spam: Confidence-Adaptive and Cost-Aware
              Spam Account Detection in Online Social Networks

This is the main entry point for the backend API.
Run with: uvicorn main:app --reload

API Endpoints:
  GET  /         → Health check
  POST /train    → Train the ML models
  POST /predict  → Predict if an account is spam or legitimate
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    AccountFeatures,
    PredictionResponse,
    TrainResponse,
    TemporalPredictionRequest,
    TemporalPredictionResponse,
)
from model import train_model, predict_spam, predict_temporal


# ─── Initialize FastAPI App ──────────────────────────────────────

app = FastAPI(
    title="CADENCE-Spam API",
    description=(
        "Confidence-Adaptive and Cost-Aware Spam Account Detection "
        "for Online Social Networks. This API uses a two-stage ML pipeline "
        "to efficiently classify social media accounts as spam or legitimate."
    ),
    version="1.0.0",
    contact={
        "name": "CADENCE-Spam Team",
        "email": "cadence-spam@snist.edu.in",
    },
)


# ─── CORS Middleware ─────────────────────────────────────────────
# Allows the frontend (React/Next.js) to communicate with this API
# In production, replace "*" with specific frontend URLs

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ─── Endpoint 1: Health Check ────────────────────────────────────


@app.get("/", tags=["Health"])
def health_check():
    """
    Health Check Endpoint

    Returns the current status of the API.
    Used to verify the server is running correctly.

    Returns:
        JSON with status, project name, and version
    """
    return {
        "status": "running",
        "project": "CADENCE-Spam",
        "description": "Confidence-Adaptive and Cost-Aware Spam Account Detection",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /",
            "train": "POST /train",
            "predict": "POST /predict",
            "predict_temporal": "POST /predict_temporal",
            "docs": "GET /docs",
        },
    }


# ─── Endpoint 2: Train Model ────────────────────────────────────


@app.post("/train", response_model=TrainResponse, tags=["Training"])
def train():
    """
    Train Model Endpoint

    Trains two Random Forest classifiers:
      - Stage 1 Model: Uses low-cost features (account_age, profile_completeness,
        posting_frequency, message_similarity, hashtag_usage)
      - Stage 2 Model: Uses all features (low-cost + malicious_url_count, follower_following_ratio)

    If no dataset exists, a synthetic dataset (1000 samples) is auto-generated.
    Trained models are saved to disk as .pkl files.

    Returns:
        TrainResponse with accuracy metrics and sample count
    """
    try:
        result = train_model()
        return TrainResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


# ─── Endpoint 3: Predict Spam ───────────────────────────────────


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(account: AccountFeatures):
    """
    Predict Spam Endpoint — Confidence-Adaptive Workflow

    Accepts account features as JSON and applies the CADENCE-Spam
    two-stage confidence-adaptive detection pipeline:

    1. Stage 1 (Low-Cost): Classify using basic features only
       → If confidence >= 0.80, return result immediately
       → If confidence <  0.80, escalate to Stage 2

    2. Stage 2 (Full Analysis): Classify using ALL features
       → Return the final, more confident result

    Sample Request Body:
    ```json
    {
        "account_age": 10,
        "profile_completeness": 0.15,
        "posting_frequency": 80.0,
        "message_similarity": 0.92,
        "hashtag_usage": 12.5,
        "malicious_url_count": 35,
        "follower_following_ratio": 0.05
    }
    ```

    Sample Response:
    ```json
    {
        "prediction": "spam",
        "confidence": 0.97,
        "analysis_stage": "low_cost"
    }
    ```

    Args:
        account: AccountFeatures Pydantic model with all 6 feature values

    Returns:
        PredictionResponse with prediction, confidence, and analysis_stage
    """
    try:
        # Convert Pydantic model to dictionary for the ML pipeline
        features = account.model_dump()

        # Run the confidence-adaptive prediction
        result = predict_spam(features)

        return PredictionResponse(**result)

    except FileNotFoundError as e:
        # Models haven't been trained yet
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ─── Endpoint 4: Predict Temporal Drift ─────────────────────────


@app.post(
    "/predict_temporal", response_model=TemporalPredictionResponse, tags=["Prediction"]
)
def predict_temporal_endpoint(request: TemporalPredictionRequest):
    """
    Predict Temporal Drift Endpoint

    Accepts a chronological list of account feature snapshots and runs the
    CADENCE-Spam pipeline on all of them to determine if the account has
    demonstrated behavioral drift (e.g., from legitimate to spam).
    """
    try:
        # Convert list of Pydantic models to list of dictionaries
        snapshots_features = [snapshot.model_dump() for snapshot in request.snapshots]

        # Run temporal prediction analysis
        result = predict_temporal(snapshots_features)

        return TemporalPredictionResponse(**result)

    except FileNotFoundError as e:
        # Models haven't been trained yet
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Temporal Prediction failed: {str(e)}"
        )


# ─── Main Entry Point ───────────────────────────────────────────
# This allows running the server directly with: python main.py

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
