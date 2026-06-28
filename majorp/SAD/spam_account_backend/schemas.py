"""
schemas.py — Pydantic Models for CADENCE-Spam
==============================================
Defines the request and response data structures used by the API.
These models handle automatic validation of incoming JSON data.
"""

from pydantic import BaseModel, Field


# ─── Request Models ───────────────────────────────────────────────

class AccountFeatures(BaseModel):
    """
    Input model representing a social network account's features.
    
    Stage 1 (Low-Cost) Features:
        - account_age: Days since the account was created
        - profile_completeness: Ratio (0 to 1) of filled profile fields
        - posting_frequency: Average posts per day
        - message_similarity: Cosine similarity score of sent messages (0 to 1)
        - hashtag_usage: Average number of hashtags used per post
    
    Stage 2 (High-Cost) Features:
        - malicious_url_count: Number of suspicious/malicious URLs shared in recent posts
        - follower_following_ratio: Followers / Following ratio
    """

    # Stage 1: Low-cost features (quick to compute)
    account_age: float = Field(
        ...,
        description="Account age in days",
        examples=[365]
    )
    profile_completeness: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Profile completeness ratio (0 = empty, 1 = fully filled)",
        examples=[0.85]
    )
    posting_frequency: float = Field(
        ...,
        ge=0.0,
        description="Average number of posts per day",
        examples=[3.5]
    )
    message_similarity: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Average similarity between user's messages (0 = unique, 1 = identical)",
        examples=[0.2]
    )
    hashtag_usage: float = Field(
        ...,
        ge=0.0,
        description="Average number of hashtags used per post",
        examples=[2.5]
    )

    # Stage 2: High-cost features (expensive to compute)
    malicious_url_count: float = Field(
        ...,
        ge=0.0,
        description="Number of suspicious/malicious URLs shared in recent posts",
        examples=[2]
    )
    follower_following_ratio: float = Field(
        ...,
        ge=0.0,
        description="Ratio of followers to following count",
        examples=[1.5]
    )


# ─── Response Models ──────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """
    Output model for the /predict endpoint.
    
    - prediction: "spam" or "legitimate"
    - confidence: ML model's confidence score (0.0 to 1.0)
    - analysis_stage: Which stage produced the final decision
        - "low_cost" = decided using Stage 1 features only
        - "full_analysis" = escalated to Stage 2 (all features used)
    """
    prediction: str = Field(
        ...,
        description="Classification result: 'spam' or 'legitimate'",
        examples=["spam"]
    )
    confidence: float = Field(
        ...,
        description="Model confidence score between 0.0 and 1.0",
        examples=[0.92]
    )
    analysis_stage: str = Field(
        ...,
        description="Stage at which the decision was made: 'low_cost' or 'full_analysis'",
        examples=["low_cost"]
    )


class TrainResponse(BaseModel):
    """
    Output model for the /train endpoint.
    
    Returns training status, accuracy metrics, and dataset information.
    """
    message: str = Field(
        ...,
        description="Status message about training outcome",
        examples=["Models trained successfully"]
    )
    stage1_accuracy: float = Field(
        ...,
        description="Accuracy of the Stage 1 (low-cost) model",
        examples=[0.89]
    )
    stage2_accuracy: float = Field(
        ...,
        description="Accuracy of the Stage 2 (full-analysis) model",
        examples=[0.94]
    )
    samples_used: int = Field(
        ...,
        description="Total number of training samples used",
        examples=[1000]
    )


class TemporalPredictionRequest(BaseModel):
    """
    Input model for the /predict_temporal endpoint.
    
    Accepts a list of AccountFeatures ordered chronologically (oldest to newest).
    This allows the system to analyze user activity over time and detect behavioral drift.
    """
    snapshots: list[AccountFeatures] = Field(
        ...,
        min_length=2,
        description="Chronological list of account feature snapshots (oldest to newest)",
    )


class TemporalPredictionResponse(BaseModel):
    """
    Output model for the /predict_temporal endpoint.
    
    - predictions: List of individual PredictionResponses for each snapshot
    - drift_detected: Boolean indicating if there was a shift from legitimate to spam
    - drift_confidence: Overall confidence of the drift assessment
    - message: Analysis summary
    """
    predictions: list[PredictionResponse] = Field(
        ...,
        description="List of predictions for each provided snapshot"
    )
    drift_detected: bool = Field(
        ...,
        description="True if behavioral drift from Legitimate to Spam was detected",
        examples=[True]
    )
    drift_confidence: float = Field(
        ...,
        description="Overall confidence score for the temporal drift assessment (0.0 to 1.0)",
        examples=[0.95]
    )
    message: str = Field(
        ...,
        description="Summary of the temporal analysis",
        examples=["Behavioral drift detected. Account transitioned from legitimate to spam-like activity."]
    )
