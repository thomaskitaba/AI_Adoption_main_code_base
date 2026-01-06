import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from pathlib import Path
import joblib


def train_rf_model(csv_path, model_path, config_path="config/modeling_config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["modeling"]

    FEATURES = config["features"]
    TARGET = config["target"]
    rf_cfg = config["random_forest"]

    df = pd.read_csv(csv_path)

    # Drop rows with missing features or target
    df = df.dropna(subset=FEATURES + [TARGET])
    if df.shape[0] == 0:
        raise ValueError("No training rows remain after dropping missing values. Check input CSV and preprocessing steps.")

    X = df[FEATURES]
    y = (df[TARGET] > 0.5).astype(int)

    if y.nunique() < 2:
        print("⚠ Only one class present in target; training a DummyClassifier that predicts the majority class for RF fallback.")
        model = DummyClassifier(strategy="most_frequent")
    else:
        model = RandomForestClassifier(**rf_cfg)

    model.fit(X, y)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"✔ RF model saved: {model_path}")
