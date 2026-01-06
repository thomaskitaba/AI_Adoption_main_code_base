from pathlib import Path
from .train_logit import train_logit_model
from .train_random_forest import train_rf_model


def run_modeling_pipeline():
    """Train and save models used by the policy simulation.

    This creates the `models/` directory and saves two models for woreda level.
    """
    print("▶ Running modeling pipeline")

    Path("models").mkdir(parents=True, exist_ok=True)

    # Train woreda models
    train_logit_model("data/ai_ready/woreda_ai_features.csv", "models/logit_woreda.pkl")
    train_rf_model("data/ai_ready/woreda_ai_features.csv", "models/rf_woreda.pkl")

    print("✔ Modeling pipeline finished")


if __name__ == "__main__":
    run_modeling_pipeline()
