#!/usr/bin/env python3
"""
Run trained AI adoption models on new data and save predictions.

Usage:
    python run_predictions.py --features_csv data/processed/woreda_ai_features.csv \
                              --output_csv data/predictions/woreda_predictions.csv \
                              --logit_model models/logit_woreda.pkl \
                              --rf_model models/rf_woreda.pkl
"""

import pandas as pd
import joblib
import argparse
import os

def main(features_csv, output_csv, logit_model_path, rf_model_path):
    # ---------------------------
    # 1. Load feature data
    # ---------------------------
    if not os.path.exists(features_csv):
        raise FileNotFoundError(f"Features CSV not found: {features_csv}")

    df = pd.read_csv(features_csv)

    # ---------------------------
    # 2. Define features used in training
    # ---------------------------
    feature_columns = [
        "avg_land_size_ha",
        "avg_farming_experience_years",
        "credit_access_rate",
        "extension_access_rate",
        "avg_distance_to_market_km",
        "avg_travel_time_to_extension"
    ]

    for col in feature_columns:
        if col not in df.columns:
            raise KeyError(f"Feature column missing in CSV: {col}")

    X = df[feature_columns]
    # ---------------------------
    # 3. Load trained models
    # ---------------------------
    if not os.path.exists(logit_model_path):
        raise FileNotFoundError(f"Logit model not found: {logit_model_path}")
    if not os.path.exists(rf_model_path):
        raise FileNotFoundError(f"RF model not found: {rf_model_path}")

    logit_model = joblib.load(logit_model_path)
    rf_model = joblib.load(rf_model_path)

    # ---------------------------
    # 4. Make predictions
    # ---------------------------
    df["logit_pred"] = logit_model.predict(X)
    df["logit_prob"] = logit_model.predict_proba(X)[:, 1] if hasattr(logit_model, "predict_proba") else df["logit_pred"]

    df["rf_pred"] = rf_model.predict(X)
    df["rf_prob"] = rf_model.predict_proba(X)[:, 1] if hasattr(rf_model, "predict_proba") else df["rf_pred"]

    # ---------------------------
    # 5. Save predictions
    # ---------------------------
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Predictions saved to: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run trained AI adoption models on new data")
    parser.add_argument("--features_csv", type=str, required=True, help="Path to AI-ready CSV features")
    parser.add_argument("--output_csv", type=str, required=True, help="Path to save predictions CSV")
    parser.add_argument("--logit_model", type=str, required=True, help="Path to trained Logistic model .pkl")
    parser.add_argument("--rf_model", type=str, required=True, help="Path to trained Random Forest model .pkl")
    args = parser.parse_args()

    main(args.features_csv, args.output_csv, args.logit_model, args.rf_model)
