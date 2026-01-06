import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from pathlib import Path
import joblib


def train_rf_model(csv_path, model_path, preprocessing=None, config_path="config/modeling_config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["modeling"]

    FEATURES = config["features"]
    TARGET = config["target"]
    rf_cfg = config["random_forest"]

    df = pd.read_csv(csv_path)

    # Default preprocessing config
    preprocessing = preprocessing or {"strategy": "drop"}
    strategy = preprocessing.get("strategy", "drop")
    imputer_cfg = preprocessing.get("imputer", {})

    # Always drop rows with missing target values
    df = df.dropna(subset=[TARGET])

    if strategy == "drop":
        df = df.dropna(subset=FEATURES)
        if df.shape[0] == 0:
            raise ValueError("No training rows remain after dropping missing values. Check input CSV and preprocessing steps.")

    # Prepare X and y
    X = df[FEATURES]
    y = (df[TARGET] > 0.5).astype(int)

    if y.nunique() < 2:
        print("⚠ Only one class present in target; training a DummyClassifier that predicts the majority class for RF fallback.")
        model = DummyClassifier(strategy="most_frequent")
    else:
        if strategy == "impute":
            imputer_strategy = imputer_cfg.get("strategy", "median")
            fill_value = imputer_cfg.get("fill_value", None)
            imputer = SimpleImputer(strategy=imputer_strategy, fill_value=fill_value)
            model = Pipeline([("imputer", imputer), ("rf", RandomForestClassifier(**rf_cfg))])
        else:
            model = RandomForestClassifier(**rf_cfg)

    model.fit(X, y)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"✔ RF model saved: {model_path}")
