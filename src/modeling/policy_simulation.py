import yaml
import pandas as pd
import joblib
from pathlib import Path
import numpy as np


def _positive_prob(m, X):
    """
    Robustly extract positive-class probability from sklearn models or Pipelines.
    For regression models, return clipped predictions.
    """
    if hasattr(m, "predict_proba"):
        probs = m.predict_proba(X)
        probs = np.asarray(probs)

        if probs.ndim == 1:
            probs = probs.reshape(-1, 1)

        # Try to read classes_
        classes = getattr(m, "classes_", None)
        if classes is None and hasattr(m, "named_steps"):
            last = list(m.named_steps.values())[-1]
            classes = getattr(last, "classes_", None)

        if classes is not None:
            classes = list(classes)
            if 1 in classes:
                return probs[:, classes.index(1)]
            return np.zeros(probs.shape[0])

        # Fallback heuristics
        if probs.shape[1] == 2:
            return probs[:, 1]
        return probs[:, 0]

    # No predict_proba → assume regression, return clipped predict
    preds = np.asarray(m.predict(X), dtype=float)
    return np.clip(preds, 0, 1)


def run_policy_simulation(config_path="config/policy_simulation.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["policy_simulation"]

    output_dir = Path(config["output"]["directory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    for level, level_cfg in config["levels"].items():
        print(f"\n▶ Running policy simulations at {level} level")

        model = joblib.load(level_cfg["model_path"])
        df = pd.read_csv(level_cfg["ai_ready_csv"])

        features = model.feature_names_in_

        for scenario, spec in config["scenarios"].items():
            print(f"  ▶ Scenario: {scenario}")

            df_cf = df.copy()

            # Apply counterfactual changes
            for var, value in spec["changes"].items():
                if var in df_cf.columns:
                    df_cf[var] = value

            # Probabilities
            p_base = _positive_prob(model, df[features])
            p_cf = _positive_prob(model, df_cf[features])

            # Assemble result
            result = df.copy()
            result["baseline_adoption_prob"] = p_base
            result["counterfactual_adoption_prob"] = p_cf
            result["policy_effect"] = p_cf - p_base
            result["scenario"] = scenario
            result["level"] = level

            out_path = output_dir / f"{scenario}_{level}.csv"
            result.to_csv(out_path, index=False)

            print(f"  ✔ Saved {out_path}")


if __name__ == "__main__":
    run_policy_simulation()
