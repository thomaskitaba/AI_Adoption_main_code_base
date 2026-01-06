import pandas as pd
import joblib

POLICY_VARS = [
    "credit_access_rate",
    "extension_access_rate",
    "avg_travel_time_to_extension"
]


def simulate_policy(
    model_path,
    data_csv,
    policy_changes: dict
):
    model = joblib.load(model_path)
    df = pd.read_csv(data_csv)

    df_cf = df.copy()

    for var, new_value in policy_changes.items():
        if var in df_cf.columns:
            df_cf[var] = new_value

    X_orig = df[model.feature_names_in_]
    X_cf = df_cf[model.feature_names_in_]

    p_orig = model.predict_proba(X_orig)[:, 1]
    p_cf = model.predict_proba(X_cf)[:, 1]

    df["baseline_adoption_prob"] = p_orig
    df["counterfactual_adoption_prob"] = p_cf
    df["policy_effect"] = p_cf - p_orig

    return df
