import geopandas as gpd
from pathlib import Path

TARGET_COLUMNS = [
    "ai_crop_advisory_adoption_rate",
    "ai_livestock_advisory_adoption_rate",
    "ai_driven_technology_adoption_rate"
]

ID_COLUMNS = ["region", "zone", "woreda", "kebele"]

FEATURE_COLUMNS = [
    "num_farmers",
    "avg_land_size_ha",
    "avg_farming_experience_years",
    "credit_access_rate",
    "extension_access_rate",
    "avg_distance_to_market_km",
    "avg_travel_time_to_extension"
]


def prepare_ai_ready_dataset(
    geojson_path: str,
    output_csv: str,
    level: str
):
    print(f"▶ Preparing AI-ready dataset ({level})")

    gdf = gpd.read_file(geojson_path)

    # Drop geometry
    df = gdf.drop(columns="geometry")

    # Select columns
    cols = ID_COLUMNS + FEATURE_COLUMNS + TARGET_COLUMNS
    cols = [c for c in cols if c in df.columns]

    df = df[cols]

    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    print(f"✔ Saved AI-ready dataset: {output_csv}")
