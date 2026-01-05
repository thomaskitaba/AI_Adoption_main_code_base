import geopandas as gpd
import pandas as pd

def kebele_geospatial_join(
    kebele_geojson_path: str,
    kebele_aggregated_csv: str,
):
    import geopandas as gpd
    import pandas as pd

    gdf = gpd.read_file(kebele_geojson_path)

    gdf = gdf.rename(columns={
        "R_NAME": "region",
        "Z_NAME": "zone",
        "W_NAME": "woreda",
        "KK_NAME": "kebele"
    })

    # Ensure kebele exists in GeoDataFrame — fallback to other name fields or synthesize
    gdf['kebele'] = gdf.get('kebele', '').fillna('').astype(str).str.strip()
    for alt in ['T_NAME', 'UK_NAME', 'RK_NAME']:
        if alt in gdf.columns:
            mask = gdf['kebele'] == ''
            if mask.any():
                gdf.loc[mask, 'kebele'] = gdf.loc[mask, alt].fillna('').astype(str).str.strip()

    mask = gdf['kebele'].astype(str).str.strip() == ''
    if mask.any():
        gdf.loc[mask, 'kebele'] = gdf.loc[mask].apply(
            lambda r: f"{r['woreda']}_unk_{r.name}", axis=1
        )

    df = pd.read_csv(kebele_aggregated_csv)

    join_keys = ["region", "zone", "woreda", "kebele"]
    for col in join_keys:
        if col not in gdf.columns or col not in df.columns:
            raise KeyError(f"Missing join column: {col}")

    gdf_joined = gdf.merge(
        df,
        on=join_keys,
        how="left",
        validate="1:1"
    )

    return gdf_joined


def join_kebele_attributes(
    kebele_geojson_path: str,
    kebele_aggregated_csv: str,
    join_key: str | None = None,
):
    """Join kebele attributes from a CSV to a GeoDataFrame.

    If `join_key` is provided and exists in both the GeoDataFrame and the
    aggregated CSV, perform a simple single-column join using that key.
    Otherwise fall back to the original composite join on
    ["region", "zone", "woreda", "kebele"].
    """
    # Read inputs
    gdf = gpd.read_file(kebele_geojson_path)
    df = pd.read_csv(kebele_aggregated_csv)

    # Normalize column names in geojson to expected names
    gdf = gdf.rename(columns={
        "R_NAME": "region",
        "Z_NAME": "zone",
        "W_NAME": "woreda",
        "KK_NAME": "kebele"
    })

    # Normalize kebele in GeoDataFrame to match generation strategy (fallbacks)
    gdf['kebele'] = gdf.get('kebele', '').fillna('').astype(str).str.strip()
    for alt in ['T_NAME', 'UK_NAME', 'RK_NAME']:
        if alt in gdf.columns:
            mask = gdf['kebele'] == ''
            if mask.any():
                gdf.loc[mask, 'kebele'] = gdf.loc[mask, alt].fillna('').astype(str).str.strip()

    mask = gdf['kebele'].astype(str).str.strip() == ''
    if mask.any():
        gdf.loc[mask, 'kebele'] = gdf.loc[mask].apply(
            lambda r: f"{r['woreda']}_unk_{r.name}", axis=1
        )

    # Attempt single-key join if requested and available
    if join_key:
        if join_key in gdf.columns and join_key in df.columns:
            gdf_joined = gdf.merge(
                df,
                on=join_key,
                how="left",
                validate="1:1"
            )
            return gdf_joined
        else:
            print(f"⚠️ join_key '{join_key}' not found in both datasets. Falling back to composite regional keys.")

    # Fallback to composite join (re-uses the checks implemented above)
    return kebele_geospatial_join(kebele_geojson_path, kebele_aggregated_csv)
