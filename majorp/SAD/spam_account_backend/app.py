"""
app.py — Flask Application for CADENCE-Spam
============================================
CADENCE-Spam: Confidence-Adaptive and Cost-Aware
              Spam Account Detection in Online Social Networks

Loads the pre-trained .pkl models and provides a beautiful web UI.
Run with: python app.py
"""

import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

# ─── Constants ────────────────────────────────────────────────────

STAGE1_MODEL_PATH = os.path.join(os.path.dirname(__file__), "stage1_model.pkl")
STAGE2_MODEL_PATH = os.path.join(os.path.dirname(__file__), "stage2_model.pkl")
CONFIDENCE_THRESHOLD = 0.80

LOW_COST_FEATURES = [
    "account_age",
    "profile_completeness",
    "posting_frequency",
    "message_similarity",
    "hashtag_usage",
]

ALL_FEATURES = LOW_COST_FEATURES + [
    "malicious_url_count",
    "follower_following_ratio",
]

# ─── Load Models ──────────────────────────────────────────────────

stage1_model = None
stage2_model = None


def load_models():
    global stage1_model, stage2_model
    try:
        stage1_model = joblib.load(STAGE1_MODEL_PATH)
        stage2_model = joblib.load(STAGE2_MODEL_PATH)
        print("✅ Models loaded successfully from .pkl files!")
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return False


# ─── Flask App ────────────────────────────────────────────────────

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main web UI page."""
    models_ready = stage1_model is not None and stage2_model is not None
    return render_template("index.html", models_ready=models_ready)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict Spam Endpoint — Confidence-Adaptive Workflow.
    Accepts form data or JSON and returns a prediction.
    """
    if stage1_model is None or stage2_model is None:
        return (
            jsonify({"error": "Models not loaded. Please ensure .pkl files exist."}),
            500,
        )

    try:
        # Accept both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Parse features
        features = {
            "account_age": float(data.get("account_age", 0)),
            "profile_completeness": float(data.get("profile_completeness", 0)),
            "posting_frequency": float(data.get("posting_frequency", 0)),
            "message_similarity": float(data.get("message_similarity", 0)),
            "hashtag_usage": float(data.get("hashtag_usage", 0)),
            "malicious_url_count": float(data.get("malicious_url_count", 0)),
            "follower_following_ratio": float(data.get("follower_following_ratio", 0)),
        }

        # 🔥 Improved spam rule
        if (
            features["posting_frequency"] > 20 and
            features["message_similarity"] > 5
        ):
            return jsonify({
                "prediction": "spam",
                "confidence": 95,
                "analysis_stage": "Rule-Based Detection",
                "reason": "Too many posts and comments"
            })

        # ── Stage 1: Low-Cost Feature Analysis ──
        stage1_input = pd.DataFrame([{k: features[k] for k in LOW_COST_FEATURES}])
        stage1_proba = stage1_model.predict_proba(stage1_input)[0]
        stage1_pred = stage1_model.predict(stage1_input)[0]
        stage1_conf = float(max(stage1_proba))

        if stage1_conf >= CONFIDENCE_THRESHOLD:
            return jsonify(
                {
                    "prediction": "spam" if stage1_pred == 1 else "legitimate",
                    "confidence": round(stage1_conf * 100, 2),
                    "analysis_stage": "Stage 1 (Low-Cost Features)",
                    "stage_icon": "⚡",
                    "stage1_conf": round(stage1_conf * 100, 2),
                    "stage2_conf": None,
                    "features": features,
                }
            )

        # ── Stage 2: Full Feature Analysis (Escalation) ──
        stage2_input = pd.DataFrame([{k: features[k] for k in ALL_FEATURES}])
        stage2_proba = stage2_model.predict_proba(stage2_input)[0]
        stage2_pred = stage2_model.predict(stage2_input)[0]
        stage2_conf = float(max(stage2_proba))

        return jsonify(
            {
                "prediction": "spam" if stage2_pred == 1 else "legitimate",
                "confidence": round(stage2_conf * 100, 2),
                "analysis_stage": "Stage 2 (Full Analysis)",
                "stage_icon": "🔬",
                "stage1_conf": round(stage1_conf * 100, 2),
                "stage2_conf": round(stage2_conf * 100, 2),
                "features": features,
            }
        )

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@app.route("/status")
def status():
    """Return model loading status."""
    return jsonify(
        {
            "stage1_model": "loaded" if stage1_model is not None else "not loaded",
            "stage2_model": "loaded" if stage2_model is not None else "not loaded",
            "stage1_path": STAGE1_MODEL_PATH,
            "stage2_path": STAGE2_MODEL_PATH,
            "stage1_exists": os.path.exists(STAGE1_MODEL_PATH),
            "stage2_exists": os.path.exists(STAGE2_MODEL_PATH),
        }
    )


# ─── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Starting CADENCE-Spam Flask Application...")
    load_models()
    app.run(debug=True, host="0.0.0.0", port=5000)
