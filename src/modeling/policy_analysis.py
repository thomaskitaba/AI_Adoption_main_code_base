import pandas as pd
import os
from pathlib import Path
import yaml

def run_policy_analysis(config_path="config/policy_simulation.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["policy_simulation"]

    output_dir = Path("data/policy_summary")
    output_dir.mkdir(parents=True, exist_ok=True)

    for level in config["levels"].keys():
        results = []
        for scenario in config["scenarios"].keys():
            if scenario == "baseline":
                continue  # Skip baseline as it has no effect
            csv_path = f"data/policy_outputs/{scenario}_{level}.csv"
            if not os.path.exists(csv_path):
                continue
            df = pd.read_csv(csv_path)
            effects = df["policy_effect"]
            result = {
                "scenario": scenario,
                "level": level,
                "mean_policy_effect": effects.mean(),
                "median_policy_effect": effects.median(),
                "pct_positive": (effects > 0).mean(),
                "max_effect": effects.max(),
                "min_effect": effects.min()
            }
            results.append(result)

        if results:
            summary_df = pd.DataFrame(results)
            out_path = output_dir / f"policy_ranking_{level}.csv"
            summary_df.to_csv(out_path, index=False)
            print(f"✔ Saved {out_path}")

if __name__ == "__main__":
    run_policy_analysis()