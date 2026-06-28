"""
model.py — Machine Learning Module for CADENCE-Spam
=====================================================
Implements the core ML logic:
  1. Training two Random Forest classifiers (Stage 1 and Stage 2)
  2. Confidence-adaptive prediction workflow

Key Concept — Confidence-Adaptive Detection:
  - Stage 1 uses only LOW-COST features for quick classification
  - If the model is confident (>= 0.80), the result is returned immediately
  - If the model is uncertain (< 0.80), it ESCALATES to Stage 2
  - Stage 2 uses ALL features (low-cost + high-cost) for a more thorough analysis
  - This approach reduces computational cost while maintaining accuracy
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from utils import (
    load_dataset,
    preprocess_data,
    generate_synthetic_dataset,
    LOW_COST_FEATURES,
    ALL_FEATURES,
    CONFIDENCE_THRESHOLD,
)


# ─── File paths for saved models ─────────────────────────────────

STAGE1_MODEL_PATH = "stage1_model.pkl"   # Trained on low-cost features only
STAGE2_MODEL_PATH = "stage2_model.pkl"   # Trained on all features
DATASET_PATH = "dataset.csv"


def train_model(filepath: str = DATASET_PATH) -> dict:
    """
    Train two Random Forest classifiers for the two-stage detection pipeline.
    
    Stage 1 Model:
        - Trained on LOW-COST features: account_age, profile_completeness,
          posting_frequency, message_similarity
        - Purpose: Quick initial classification of obvious spam/legitimate accounts
    
    Stage 2 Model:
        - Trained on ALL features (low-cost + high-cost)
        - Purpose: Deeper analysis for ambiguous cases that Stage 1 couldn't decide
    
    Both models are saved to disk as .pkl files using joblib.
    
    Args:
        filepath: Path to the training dataset CSV
        
    Returns:
        Dictionary with training results (accuracy scores, sample count)
    """
    
    # ── Step 1: Generate dataset if it doesn't exist ──
    if not os.path.exists(filepath):
        print("📊 No dataset found. Generating synthetic dataset...")
        generate_synthetic_dataset(n_samples=1000, filepath=filepath)
    
    # ── Step 2: Load and preprocess data ──
    X, y = load_dataset(filepath)
    X = preprocess_data(X)
    
    # ── Step 3: Split into training and testing sets (80/20 split) ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # ── Step 4: Train Stage 1 Model (Low-Cost Features Only) ──
    print("\n🔹 Training Stage 1 Model (Low-Cost Features)...")
    
    # Extract only low-cost features for Stage 1
    X_train_stage1 = X_train[LOW_COST_FEATURES]
    X_test_stage1 = X_test[LOW_COST_FEATURES]
    
    stage1_model = RandomForestClassifier(
        n_estimators=100,     # Number of decision trees in the forest
        max_depth=10,         # Maximum depth of each tree (prevents overfitting)
        random_state=42,      # Reproducible results
        n_jobs=-1,            # Use all CPU cores for faster training
    )
    stage1_model.fit(X_train_stage1, y_train)
    
    # Evaluate Stage 1
    stage1_predictions = stage1_model.predict(X_test_stage1)
    stage1_accuracy = accuracy_score(y_test, stage1_predictions)
    print(f"   ✅ Stage 1 Accuracy: {stage1_accuracy:.4f}")
    
    # ── Step 5: Train Stage 2 Model (All Features) ──
    print("\n🔹 Training Stage 2 Model (All Features)...")
    
    stage2_model = RandomForestClassifier(
        n_estimators=150,     # More trees for better accuracy with more features
        max_depth=12,         # Slightly deeper trees for complex patterns
        random_state=42,
        n_jobs=-1,
    )
    stage2_model.fit(X_train[ALL_FEATURES], y_train)
    
    # Evaluate Stage 2
    stage2_predictions = stage2_model.predict(X_test[ALL_FEATURES])
    stage2_accuracy = accuracy_score(y_test, stage2_predictions)
    print(f"   ✅ Stage 2 Accuracy: {stage2_accuracy:.4f}")
    
    # ── Step 6: Save models to disk ──
    joblib.dump(stage1_model, STAGE1_MODEL_PATH)
    joblib.dump(stage2_model, STAGE2_MODEL_PATH)
    print(f"\n💾 Models saved: {STAGE1_MODEL_PATH}, {STAGE2_MODEL_PATH}")
    
    return {
        "message": "Models trained successfully",
        "stage1_accuracy": round(stage1_accuracy, 4),
        "stage2_accuracy": round(stage2_accuracy, 4),
        "samples_used": len(X),
    }


def predict_spam(features: dict) -> dict:
    """
    Confidence-Adaptive Spam Detection — The core CADENCE-Spam workflow.
    
    This function implements the two-stage adaptive detection pipeline:
    
    ┌─────────────────────────────────────────────────────┐
    │  INPUT: Account features (all 6 values)             │
    │                                                     │
    │  STAGE 1: Use low-cost features only                │
    │     → Run Stage 1 ML model                          │
    │     → Get prediction + confidence score             │
    │                                                     │
    │  DECISION:                                          │
    │     IF confidence >= 0.80 → RETURN result (done!)   │
    │     IF confidence <  0.80 → ESCALATE to Stage 2     │
    │                                                     │
    │  STAGE 2: Use ALL features (low-cost + high-cost)   │
    │     → Run Stage 2 ML model                          │
    │     → Get final prediction + confidence score       │
    │     → RETURN result                                 │
    └─────────────────────────────────────────────────────┘
    
    Args:
        features: Dictionary with all 6 account features
        
    Returns:
        Dictionary with prediction, confidence, and analysis_stage
    """
    
    # ── Verify models exist ──
    if not os.path.exists(STAGE1_MODEL_PATH) or not os.path.exists(STAGE2_MODEL_PATH):
        raise FileNotFoundError(
            "Models not found. Please train the models first by calling POST /train"
        )
    
    # ── Load saved models ──
    stage1_model = joblib.load(STAGE1_MODEL_PATH)
    stage2_model = joblib.load(STAGE2_MODEL_PATH)
    
    # ══════════════════════════════════════════════════════
    # STAGE 1: Low-Cost Feature Analysis
    # ══════════════════════════════════════════════════════
    
    # Extract only the low-cost features for Stage 1
    stage1_features = {key: features[key] for key in LOW_COST_FEATURES}
    stage1_input = pd.DataFrame([stage1_features])
    
    # Get prediction probabilities from Stage 1 model
    # predict_proba returns [P(legitimate), P(spam)] for each sample
    stage1_probabilities = stage1_model.predict_proba(stage1_input)[0]
    stage1_prediction = stage1_model.predict(stage1_input)[0]
    stage1_confidence = float(max(stage1_probabilities))  # Highest probability = confidence
    
    print(f"\n🔍 Stage 1 Analysis:")
    print(f"   Prediction: {'spam' if stage1_prediction == 1 else 'legitimate'}")
    print(f"   Confidence: {stage1_confidence:.4f}")
    
    # ── CONFIDENCE CHECK ──
    # If confidence is HIGH enough, return Stage 1 result immediately
    # This saves the cost of computing high-cost features
    if stage1_confidence >= CONFIDENCE_THRESHOLD:
        print(f"   ✅ Confidence >= {CONFIDENCE_THRESHOLD} → Returning Stage 1 result")
        return {
            "prediction": "spam" if stage1_prediction == 1 else "legitimate",
            "confidence": round(stage1_confidence, 4),
            "analysis_stage": "low_cost",
        }
    
    # ══════════════════════════════════════════════════════
    # STAGE 2: Full Feature Analysis (Escalation)
    # ══════════════════════════════════════════════════════
    
    print(f"\n   ⚠️ Confidence < {CONFIDENCE_THRESHOLD} → Escalating to Stage 2")
    
    # Use ALL features (low-cost + high-cost) for deeper analysis
    stage2_features = {key: features[key] for key in ALL_FEATURES}
    stage2_input = pd.DataFrame([stage2_features])
    
    # Get prediction probabilities from Stage 2 model
    stage2_probabilities = stage2_model.predict_proba(stage2_input)[0]
    stage2_prediction = stage2_model.predict(stage2_input)[0]
    stage2_confidence = float(max(stage2_probabilities))
    
    print(f"\n🔍 Stage 2 Analysis:")
    print(f"   Prediction: {'spam' if stage2_prediction == 1 else 'legitimate'}")
    print(f"   Confidence: {stage2_confidence:.4f}")
    print(f"   ✅ Returning Stage 2 (full analysis) result")
    
    return {
        "prediction": "spam" if stage2_prediction == 1 else "legitimate",
        "confidence": round(stage2_confidence, 4),
        "analysis_stage": "full_analysis",
    }


def predict_temporal(snapshots_features: list[dict]) -> dict:
    """
    Temporal Consistency Validation — Analyzes a sequence of account snapshots over time.
    
    This function processes multiple historical snapshots of an account to detect 
    behavioral drift (e.g., an established legitimate account suddenly exhibiting 
    spam-like behavior).
    
    Args:
        snapshots_features: List of dictionaries, each containing all features for a specific time snapshot.
                            Ordered from oldest to newest.
        
    Returns:
        Dictionary with drift analysis results and individual predictions.
    """
    predictions = []
    
    # Process each snapshot through the standard confidence-adaptive pipeline
    for i, features in enumerate(snapshots_features):
        print(f"\n⏳ Processing Snapshot {i + 1}/{len(snapshots_features)}")
        pred_result = predict_spam(features)
        predictions.append(pred_result)
        
    # Analyze predictions for behavioral drift (Legitimate -> Spam)
    drift_detected = False
    drift_confidence = 0.0
    message = "Account behavior has remained consistent over time."
    
    # Simple drift detection: Check if it transitioned from legitimate to spam
    # and stayed spam in the latest snapshot.
    labels = [p["prediction"] for p in predictions]
    
    if len(labels) >= 2:
        oldest_label = labels[0]
        newest_label = labels[-1]
        
        if oldest_label == "legitimate" and newest_label == "spam":
            drift_detected = True
            # The confidence of the drift is a function of the confidence in the new spam prediction
            drift_confidence = predictions[-1]["confidence"]
            message = "⚠️ WARNING: Behavioral drift detected. The account transitioned from legitimate to spam-like activity."
        elif oldest_label == "spam" and newest_label == "legitimate":
            message = "Account transitioned from spam-like behavior to legitimate behavior."
        elif oldest_label == "spam" and newest_label == "spam":
            message = "Account has consistently exhibited spam-like behavior."
        else:
            message = "Account has consistently exhibited legitimate behavior."
            
    return {
        "predictions": predictions,
        "drift_detected": drift_detected,
        "drift_confidence": round(drift_confidence, 4),
        "message": message
    }
