from pathlib import Path
import yaml
from .train_logit import train_logit_model
from .train_random_forest import train_rf_model


def run_modeling_pipeline():
    print("▶ Running modeling pipeline")

    with open("config/modeling_config.yaml") as f:
        config = yaml.safe_load(f)["modeling"]

    csv_path = config["data"]["input_csv"]
    level = config["level"]

    Path("models").mkdir(parents=True, exist_ok=True)

    train_logit_model(
        csv_path,
        f"models/logit_{level}.pkl"
    )

    train_rf_model(
        csv_path,
        f"models/rf_{level}.pkl"
    )

    print("✔ Modeling pipeline finished")


if __name__ == "__main__":
    run_modeling_pipeline()
