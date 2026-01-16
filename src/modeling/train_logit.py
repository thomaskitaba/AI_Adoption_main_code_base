import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from pathlib import Path
import joblib


def train_logit_model(csv_path, model_path, preprocessing=None, config_path="config/modeling_config.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["modeling"]

    FEATURES = config["features"]
    TARGET = config["target"]
    logit_cfg = config["logit"]

    df = pd.read_csv(csv_path)

    # Default preprocessing config
    preprocessing = preprocessing or {"strategy": "drop"}
    strategy = preprocessing.get("strategy", "drop")
    imputer_cfg = preprocessing.get("imputer", {})

    # Always drop rows with missing target values
    df = df.dropna(subset=[TARGET])

    if strategy == "drop":
        # Drop rows with missing FEATURE values
        df = df.dropna(subset=FEATURES)
        if df.shape[0] == 0:
            raise ValueError("No training rows remain after dropping missing values. Check input CSV and preprocessing steps.")

        X = df[FEATURES]
        y = df[TARGET]

        if y.nunique() < 2:
            print("⚠ Only one unique value in target; training a DummyRegressor that predicts the mean.")
            model = Pipeline([
                ("scaler", StandardScaler()),
                ("dummy", DummyRegressor(strategy="mean"))
            ])
        else:
            model = Pipeline([
                ("scaler", StandardScaler()),
                ("regressor", LinearRegression())
            ])

    elif strategy == "impute":
        # Impute missing feature values and keep rows (but still drop missing target rows earlier)
        X = df[FEATURES]
        y = df[TARGET]

        imputer_strategy = imputer_cfg.get("strategy", "median")
        fill_value = imputer_cfg.get("fill_value", None)
        imputer = SimpleImputer(strategy=imputer_strategy, fill_value=fill_value)

        steps = [("imputer", imputer), ("scaler", StandardScaler())]

        if y.nunique() < 2:
            print("⚠ Only one unique value in target; training a DummyRegressor that predicts the mean.")
            steps.append(("dummy", DummyRegressor(strategy="mean")))
        else:
            steps.append(("regressor", LinearRegression()))

        model = Pipeline(steps)

    else:
        raise ValueError(f"Unknown missing value strategy: {strategy}")

    model.fit(X, y)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"✔ Regression model saved: {model_path}")
