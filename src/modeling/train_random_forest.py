import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path
import joblib

TARGET = "ai_driven_technology_adoption_rate"

FEATURES = [
    "credit_access_rate",
    "extension_access_rate",
    "avg_travel_time_to_extension",
    "avg_land_size_ha",
    "avg_farming_experience_years",
    "avg_distance_to_market_km"
]


def train_rf_model(csv_path, model_path):
    df = pd.read_csv(csv_path)

    X = df[FEATURES]
    y = (df[TARGET] > 0.5).astype(int)

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        random_state=42
    )

    model.fit(X, y)
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"✔ RF model saved: {model_path}")
