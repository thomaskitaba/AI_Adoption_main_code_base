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

    # ---------------- Resolve level columns ----------------
    level_cols = rules["levels"][level_name]
    weight_col = rules["weights"]["default"]
    variable_rules = rules["variables"]

    # ---------------- Build aggregation dictionary ----------------
    agg_dict = {}

    for group_name, vars_in_group in variable_rules.items():
        for var, rule in vars_in_group.items():

            # Skip aggregating dissolve-by columns (they are used for grouping and
            # will be present in the result already)
            if var in level_cols:
                continue

            # Simple aggregations
            if rule in ("sum", "first"):
                agg_dict[var] = rule

            # Weighted mean aggregations
            elif isinstance(rule, dict) and rule.get("method") == "weighted_mean":
                agg_dict[var] = lambda x, v=var: weighted_mean(
                    x,
                    gdf.loc[x.index, weight_col]
                )

    # Keep dissolve-by columns (they are required for grouping).
    # Do not drop them before calling dissolve.

    # ---------------- Dissolve geometry and attributes ----------------
    dissolved = gdf.dissolve(
        by=level_cols,
        aggfunc=agg_dict,
        as_index=False
    )

    return dissolved
