"""
generate_dataset.py — Standalone Dataset Generator
====================================================
Run this script directly to generate a synthetic training dataset.

Usage:
    python generate_dataset.py

This creates 'dataset.csv' with 1000 samples (500 spam + 500 legitimate).
The /train endpoint also auto-generates this if it doesn't exist.
"""

from utils import generate_synthetic_dataset

if __name__ == "__main__":
    print("=" * 60)
    print("  CADENCE-Spam: Synthetic Dataset Generator")
    print("=" * 60)
    
    filepath = generate_synthetic_dataset(n_samples=1000, filepath="dataset.csv")
    
    print(f"\n✅ Dataset saved to: {filepath}")
    print("   You can now train the model using POST /train")
    print("=" * 60)
