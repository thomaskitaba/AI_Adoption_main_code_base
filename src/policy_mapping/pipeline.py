import geopandas as gpd
import pandas as pd
from pathlib import Path
import yaml


def run_policy_mapping(config_path="config/policy_simulation.yaml"):
    with open(config_path) as f:
        config = yaml.safe_load(f)["policy_simulation"]

    output_dir = Path("data/policy_maps")
    output_dir.mkdir(parents=True, exist_ok=True)

    for level in config["levels"].keys():
        print(f"\n▶ Mapping policy effects at {level} level")

        base_geo = f"data/processed/{level}_ai_adoption.geojson"

        for scenario in config["scenarios"].keys():
            csv_path = f"data/policy_outputs/{scenario}_{level}.csv"

            if not Path(csv_path).exists():
                continue

            gdf = gpd.read_file(base_geo)
            df = pd.read_csv(csv_path)

            join_key = level

            gdf = gdf.merge(
                df[[join_key, "policy_effect", "baseline_adoption_prob",
                    "counterfactual_adoption_prob", "scenario"]],
                on=join_key,
                how="left"
            )

            out_path = output_dir / f"{scenario}_{level}.geojson"
            gdf.to_file(out_path, driver="GeoJSON")

            print(f"✔ Saved {out_path}")
