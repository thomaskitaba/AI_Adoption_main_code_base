import pandas as pd
import numpy as np
from pathlib import Path
import yaml


def gini(x):
    x = np.asarray(x)
    if np.all(x == 0):
        return 0
    x = np.sort(x)
    n = len(x)
    cumx = np.cumsum(x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n


def run_policy_equity(config_path="config/policy_simulation.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["policy_simulation"]

    out_dir = Path("data/policy_equity")
    out_dir.mkdir(parents=True, exist_ok=True)

    for level in config["levels"].keys():
        print(f"\n▶ Equity analysis at {level} level")

        results = []

        for scenario in config["scenarios"].keys():
            path = Path(f"data/policy_outputs/{scenario}_{level}.csv")
            if not path.exists():
                continue

            df = pd.read_csv(path)
            pe = df["policy_effect"]

            results.append({
                "scenario": scenario,
                "level": level,
                "mean_effect": pe.mean(),
                "std_effect": pe.std(),
                "p90_p10_gap": pe.quantile(0.9) - pe.quantile(0.1),
                "gini_effect": gini(pe),
                "pct_negative": (pe <= 0).mean()
            })

        equity_df = pd.DataFrame(results)
        equity_df = equity_df.sort_values("gini_effect")

        out_path = out_dir / f"equity_metrics_{level}.csv"
        equity_df.to_csv(out_path, index=False)

        print(f"✔ Saved {out_path}")
