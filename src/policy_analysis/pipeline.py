import pandas as pd
from pathlib import Path
import yaml


def run_policy_comparison(config_path="config/policy_simulation.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["policy_simulation"]

    output_dir = Path("data/policy_summary")
    output_dir.mkdir(parents=True, exist_ok=True)

    for level in config["levels"].keys():
        print(f"\n▶ Comparing policies at {level} level")

        summaries = []

        for scenario in config["scenarios"].keys():
            csv_path = Path(f"data/policy_outputs/{scenario}_{level}.csv")
            if not csv_path.exists():
                continue

            df = pd.read_csv(csv_path)

            summaries.append({
                "scenario": scenario,
                "level": level,
                "mean_policy_effect": df["policy_effect"].mean(),
                "median_policy_effect": df["policy_effect"].median(),
                "pct_positive": (df["policy_effect"] > 0).mean(),
                "max_effect": df["policy_effect"].max(),
                "min_effect": df["policy_effect"].min()
            })

        summary_df = pd.DataFrame(summaries)
        summary_df = summary_df.sort_values(
            by="mean_policy_effect", ascending=False
        )

        out_path = output_dir / f"policy_ranking_{level}.csv"
        summary_df.to_csv(out_path, index=False)

        print(f"✔ Saved {out_path}")
