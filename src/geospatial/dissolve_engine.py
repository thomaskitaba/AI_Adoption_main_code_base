import geopandas as gpd
import pandas as pd


def weighted_mean(series, weights):
    """Compute weighted mean safely."""
    if series.isna().all():
        return None
    return (series * weights).sum() / weights.sum()


def dissolve_level(
    gdf: gpd.GeoDataFrame,
    level_name: str,
    rules: dict
) -> gpd.GeoDataFrame:
    """
    Dissolve a GeoDataFrame to a higher administrative level
    using rules defined in dissolve_rules.yaml.
    """

    level_cols = rules["levels"][level_name]
    weight_col = rules["weights"]["default"]
    variable_rules = rules["variables"]

    agg_dict = {}

    # ---- Build aggregation dictionary ----
    for group_name, vars_in_group in variable_rules.items():
        for var, rule in vars_in_group.items():

            # Skip variables that are already the grouping keys (they'll be present after groupby)
            if var in level_cols:
                continue

            # Simple aggregations
            if rule == "sum" or rule == "first":
                agg_dict[var] = rule

            # Weighted mean aggregations
            elif isinstance(rule, dict) and rule.get("method") == "weighted_mean":
                # Use weights if available, otherwise fall back to unweighted mean
                if weight_col in gdf.columns:
                    agg_dict[var] = lambda x, v=var: weighted_mean(
                        x,
                        gdf.loc[x.index, weight_col]
                    )
                else:
                    # fall back to simple mean if weights are missing
                    agg_dict[var] = lambda x, v=var: x.mean()
                    print(f"⚠️ weight column '{weight_col}' not found; using unweighted mean for '{var}'")

    # Filter agg_dict to variables that actually exist in gdf to avoid KeyError
    existing_cols = set(gdf.columns)
    valid_agg_dict = {k: v for k, v in agg_dict.items() if k in existing_cols}
    missing = sorted(set(agg_dict) - set(valid_agg_dict))
    if missing:
        print(f"⚠️ The following variables are not present in the GeoDataFrame and will be skipped: {missing}")
    agg_dict = valid_agg_dict

    # ---- Dissolve geometry and attributes ----
    dissolved = gdf.dissolve(
        by=level_cols,
        aggfunc=agg_dict,
        as_index=False
    )

    return dissolved
