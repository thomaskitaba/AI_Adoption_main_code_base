import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from pathlib import Path
import joblib


def train_logit_model(csv_path, model_path, config_path="config/modeling_config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["modeling"]

    FEATURES = config["features"]
    TARGET = config["target"]
    logit_cfg = config["logit"]

    df = pd.read_csv(csv_path)

    # Drop rows with missing features or target to avoid NaNs during training
    df = df.dropna(subset=FEATURES + [TARGET])
    if df.shape[0] == 0:
        raise ValueError("No training rows remain after dropping missing values. Check input CSV and preprocessing steps.")

    X = df[FEATURES]
    y = (df[TARGET] > 0.5).astype(int)

    if y.nunique() < 2:
        print("⚠ Only one class present in target; training a DummyClassifier that predicts the majority class.")
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("dummy", DummyClassifier(strategy="most_frequent"))
        ])
    else:
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("logit", LogisticRegression(**logit_cfg))
        ])

    model.fit(X, y)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"✔ Logistic model saved: {model_path}")
