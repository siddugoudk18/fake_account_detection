import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import train, predict, predict_temporal_endpoint
from schemas import AccountFeatures, TemporalPredictionRequest

print("1. Testing training...")
train_res = train()
print("Train response:", train_res)

print("\n2. Testing /predict with stage 1 confident payload...")
feat1 = AccountFeatures(
    account_age=365,
    profile_completeness=0.9,
    posting_frequency=1.2,
    message_similarity=0.1,
    hashtag_usage=0.5,
    malicious_url_count=0,
    follower_following_ratio=2.0
)
pred1 = predict(feat1)
print("Prediction response:", pred1)

print("\n3. Testing /predict_temporal with drift payload...")
feat2 = AccountFeatures(
    account_age=365+30,
    profile_completeness=0.9,
    posting_frequency=80.0,
    message_similarity=0.95,
    hashtag_usage=12.0,
    malicious_url_count=40,
    follower_following_ratio=0.1
)

drift_req = TemporalPredictionRequest(snapshots=[feat1, feat2])
temporal_pred = predict_temporal_endpoint(drift_req)
print("Temporal Drift Response:", temporal_pred)
