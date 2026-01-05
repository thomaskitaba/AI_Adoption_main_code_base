import pandas as pd
import yaml
from .aggregation_engine import build_agg_dict

def run_aggregation_memory_safe(
    input_path: str,
    outputs: dict,
    chunk_size: int
):
    with open("config/aggregation_rules.yaml") as f:
        rules = yaml.safe_load(f)

    agg_dict = build_agg_dict(rules)

    groupings = {
        "kebele": ["region", "zone", "woreda", "kebele"],
        "woreda": ["region", "zone", "woreda"],
        "zone": ["region", "zone"],
        "region": ["region"],
    }

    regions = pd.read_csv(input_path, usecols=["region"])["region"].unique()

    for level, group_cols in groupings.items():
        print(f"\n▶ Aggregating: {level}")
        results = []

        for region in regions:
            chunks = []
            for chunk in pd.read_csv(input_path, chunksize=chunk_size):
                chunk = chunk[chunk["region"] == region]
                if not chunk.empty:
                    chunks.append(chunk)

            if chunks:
                region_df = pd.concat(chunks)
                agg = (
                    region_df
                    .groupby(group_cols)
                    .agg(agg_dict)
                    .reset_index()
                )
                results.append(agg)

        final = pd.concat(results)
        final.to_csv(outputs[level], index=False)
        print(f"✔ Saved {outputs[level]}")
