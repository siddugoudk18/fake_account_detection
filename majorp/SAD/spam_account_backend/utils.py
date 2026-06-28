"""
utils.py — Helper Functions for CADENCE-Spam
=============================================
Contains utility functions for:
  1. Generating a synthetic dataset with realistic spam/legitimate patterns
  2. Loading and preprocessing the dataset for ML training
"""

import os
import numpy as np
import pandas as pd


# ─── Feature Definitions ─────────────────────────────────────────

# Stage 1: Low-cost features (quick to extract from user profile)
LOW_COST_FEATURES = [
    "account_age",            # Days since account creation
    "profile_completeness",   # Ratio of filled profile fields (0.0 - 1.0)
    "posting_frequency",      # Average posts per day
    "message_similarity",     # Similarity score of user's messages (0.0 - 1.0)
    "hashtag_usage",          # Average number of hashtags used per post
]

# Stage 2: High-cost features (require deeper analysis / API calls)
HIGH_COST_FEATURES = [
    "malicious_url_count",       # Number of suspicious/malicious URLs shared in recent posts
    "follower_following_ratio",  # Followers / Following ratio
]

# All features combined
ALL_FEATURES = LOW_COST_FEATURES + HIGH_COST_FEATURES

# Confidence threshold for the adaptive decision
# If Stage 1 confidence >= this value, no escalation is needed
CONFIDENCE_THRESHOLD = 0.80


def generate_synthetic_dataset(n_samples: int = 1000, filepath: str = "dataset.csv") -> str:
    """
    Generate a synthetic dataset with realistic spam and legitimate account patterns.
    
    Spam accounts typically have:
        - Low account age (newly created)
        - Low profile completeness (minimal effort to fill profile)
        - High posting frequency (automated/bot behavior)
        - High message similarity (copy-paste / template messages)
        - High hashtag usage (trending tags for visibility)
        - High malicious URL count (sharing malicious/promotional/shortened links)
        - Low follower-following ratio (few followers, follows many)
    
    Legitimate accounts typically have:
        - Higher account age (established accounts)
        - Higher profile completeness (real users fill profiles)
        - Moderate posting frequency (natural posting habits)
        - Lower message similarity (diverse, original content)
        - Normal hashtag usage (occasional and context-specific)
        - Lower malicious URL count (mostly clean links)
        - Higher follower-following ratio (organic follower growth)
    
    Args:
        n_samples: Total number of samples to generate (50% spam, 50% legitimate)
        filepath: Path to save the generated CSV file
        
    Returns:
        filepath: Path to the saved CSV file
    """
    np.random.seed(42)  # Reproducible results for demo purposes
    
    n_spam = n_samples // 2
    n_legit = n_samples - n_spam

    # ── Generate SPAM account features ──
    spam_data = {
        "account_age": np.random.uniform(1, 60, n_spam),             # 1-60 days (new accounts)
        "profile_completeness": np.random.uniform(0.0, 0.3, n_spam), # Barely filled profiles
        "posting_frequency": np.random.uniform(30, 100, n_spam),     # Very high posting rate
        "message_similarity": np.random.uniform(0.7, 1.0, n_spam),  # Repetitive messages
        "hashtag_usage": np.random.uniform(5.0, 15.0, n_spam),      # Abuse of hashtags
        "malicious_url_count": np.random.uniform(15, 50, n_spam),              # Many malicious URLs
        "follower_following_ratio": np.random.uniform(0.0, 0.2, n_spam),  # Low ratio
        "label": 1,  # 1 = spam
    }

    # ── Generate LEGITIMATE account features ──
    legit_data = {
        "account_age": np.random.uniform(100, 3650, n_legit),         # 100 days to 10 years
        "profile_completeness": np.random.uniform(0.6, 1.0, n_legit), # Well-filled profiles
        "posting_frequency": np.random.uniform(0.5, 15, n_legit),     # Moderate posting
        "message_similarity": np.random.uniform(0.0, 0.4, n_legit),   # Unique messages
        "hashtag_usage": np.random.uniform(0.0, 3.0, n_legit),        # Normal hashtag use
        "malicious_url_count": np.random.uniform(0, 8, n_legit),                # Few URLs
        "follower_following_ratio": np.random.uniform(0.5, 5.0, n_legit),  # Healthy ratio
        "label": 0,  # 0 = legitimate
    }

    # ── Combine and shuffle ──
    spam_df = pd.DataFrame(spam_data)
    legit_df = pd.DataFrame(legit_data)
    dataset = pd.concat([spam_df, legit_df], ignore_index=True)
    dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle

    # ── Round values for readability ──
    for col in ALL_FEATURES:
        dataset[col] = dataset[col].round(4)

    # ── Save to CSV ──
    dataset.to_csv(filepath, index=False)
    print(f"✅ Dataset generated: {filepath} ({len(dataset)} samples)")
    
    return filepath


def load_dataset(filepath: str = "dataset.csv") -> tuple:
    """
    Load dataset from CSV and split into features (X) and labels (y).
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        X: DataFrame of features
        y: Series of labels (0 = legitimate, 1 = spam)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at '{filepath}'. "
            "Please run the /train endpoint first to generate the dataset."
        )
    
    df = pd.read_csv(filepath)
    print(f"📂 Dataset loaded: {len(df)} samples")
    
    # Separate features and labels
    X = df[ALL_FEATURES]
    y = df["label"]
    
    return X, y


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic preprocessing: handle missing values and ensure correct data types.
    
    In production, this would include:
        - Outlier detection and removal
        - Feature scaling/normalization
        - Encoding categorical variables
    
    For this project, the synthetic data is already clean,
    but this function demonstrates proper pipeline structure.
    
    Args:
        df: Raw feature DataFrame
        
    Returns:
        df: Cleaned feature DataFrame
    """
    # Fill any missing values with column median (robust to outliers)
    df = df.fillna(df.median())
    
    # Ensure all values are float for ML model compatibility
    df = df.astype(float)
    
    print(f"🔧 Preprocessing complete: {df.shape[0]} rows, {df.shape[1]} columns")
    
    return df
