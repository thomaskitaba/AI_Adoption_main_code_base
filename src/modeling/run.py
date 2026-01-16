from pathlib import Path
import yaml
from .train_logit import train_logit_model
from .train_random_forest import train_rf_model


def run_modeling_pipeline():
    print("▶ Running modeling pipeline")

    with open("config/modeling_config.yaml") as f:
        config = yaml.safe_load(f)["modeling"]

    # Read global pipeline preprocessing config to determine missing-value handling
    with open("config/pipeline_config.yaml") as f:
        pipeline_cfg = yaml.safe_load(f)

    preprocessing_cfg = pipeline_cfg.get("preprocessing", {}).get("missing_values", {"strategy": "drop"})

    levels = ['woreda', 'zone', 'region']

    Path("models").mkdir(parents=True, exist_ok=True)

    for level in levels:
        csv_path = f"data/ai_ready/{level}_ai_features.csv"
        print(f"  ▶ Training models for {level} level")

        train_logit_model(
            csv_path,
            f"models/logit_{level}.pkl",
            preprocessing=preprocessing_cfg
        )

        train_rf_model(
            csv_path,
            f"models/rf_{level}.pkl",
            preprocessing=preprocessing_cfg
        )

    print("Empty columns handled according to preprocessing config: ", preprocessing_cfg)
    print("✔ Modeling pipeline finished")


if __name__ == "__main__":
    run_modeling_pipeline()
