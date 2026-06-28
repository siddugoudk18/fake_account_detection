"""
retrain_models.py — Re-train and save fresh .pkl models
=========================================================
Run this once to regenerate compatible .pkl files:
    python retrain_models.py
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ── Features ──────────────────────────────────────────────────────
LOW_COST_FEATURES = [
    "account_age",
    "profile_completeness",
    "posting_frequency",
    "message_similarity",
    "hashtag_usage",
]
HIGH_COST_FEATURES = [
    "malicious_url_count",
    "follower_following_ratio",
]
ALL_FEATURES = LOW_COST_FEATURES + HIGH_COST_FEATURES
DATASET_PATH = "dataset.csv"
STAGE1_MODEL_PATH = "stage1_model.pkl"
STAGE2_MODEL_PATH = "stage2_model.pkl"


# ── Generate Dataset ──────────────────────────────────────────────
def generate_dataset(n_samples=1000):
    np.random.seed(42)
    n_spam = n_samples // 2
    n_legit = n_samples - n_spam

    spam = {
        "account_age": np.random.uniform(1, 60, n_spam),
        "profile_completeness": np.random.uniform(0.0, 0.3, n_spam),
        "posting_frequency": np.random.uniform(30, 100, n_spam),
        "message_similarity": np.random.uniform(0.7, 1.0, n_spam),
        "hashtag_usage": np.random.uniform(5.0, 15.0, n_spam),
        "malicious_url_count": np.random.uniform(15, 50, n_spam),
        "follower_following_ratio": np.random.uniform(0.0, 0.2, n_spam),
        "label": 1,
    }
    legit = {
        "account_age": np.random.uniform(100, 3650, n_legit),
        "profile_completeness": np.random.uniform(0.6, 1.0, n_legit),
        "posting_frequency": np.random.uniform(0.5, 15, n_legit),
        "message_similarity": np.random.uniform(0.0, 0.4, n_legit),
        "hashtag_usage": np.random.uniform(0.0, 3.0, n_legit),
        "malicious_url_count": np.random.uniform(0, 8, n_legit),
        "follower_following_ratio": np.random.uniform(0.5, 5.0, n_legit),
        "label": 0,
    }

    df = pd.concat([pd.DataFrame(spam), pd.DataFrame(legit)], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(DATASET_PATH, index=False)
    print(f"✅ Dataset saved: {DATASET_PATH}  ({len(df)} samples)")
    return df


# ── Train & Save Models ───────────────────────────────────────────
def train_and_save():
    if not os.path.exists(DATASET_PATH):
        print("📊 No dataset found — generating synthetic dataset…")
        df = generate_dataset()
    else:
        df = pd.read_csv(DATASET_PATH)
        print(f"📂 Loaded existing dataset: {len(df)} samples")

    X = df[ALL_FEATURES].astype(float)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Stage 1
    print("\n🔹 Training Stage 1 model (low-cost features)…")
    m1 = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    )
    m1.fit(X_train[LOW_COST_FEATURES], y_train)
    acc1 = accuracy_score(y_test, m1.predict(X_test[LOW_COST_FEATURES]))
    joblib.dump(m1, STAGE1_MODEL_PATH)
    print(f"   ✅ Stage 1 Accuracy: {acc1:.4f}  →  saved to {STAGE1_MODEL_PATH}")

    # Stage 2
    print("\n🔹 Training Stage 2 model (all features)…")
    m2 = RandomForestClassifier(
        n_estimators=150, max_depth=12, random_state=42, n_jobs=-1
    )
    m2.fit(X_train[ALL_FEATURES], y_train)
    acc2 = accuracy_score(y_test, m2.predict(X_test[ALL_FEATURES]))
    joblib.dump(m2, STAGE2_MODEL_PATH)
    print(f"   ✅ Stage 2 Accuracy: {acc2:.4f}  →  saved to {STAGE2_MODEL_PATH}")

    print("\n🎉 Both models saved successfully! You can now run: python app.py")


if __name__ == "__main__":
    import sklearn

    print(f"scikit-learn version: {sklearn.__version__}")
    train_and_save()
