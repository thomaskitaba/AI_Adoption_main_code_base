import yaml
from pathlib import Path
import geopandas as gpd

from .join_engine import join_kebele_attributes
from .dissolve_engine import dissolve_level


def run_geospatial_pipeline():
    # ---------------- Load configs ----------------
    with open("config/pipeline_config.yaml") as f:
        config = yaml.safe_load(f)

    with open("config/dissolve_rules.yaml") as f:
        dissolve_rules = yaml.safe_load(f)

    geojson_path = (
        config["data"]["geojson"]["sample"]
        if config["run_mode"]["use_sample"]
        else config["data"]["geojson"]["full"]
    )

    kebele_csv = config["data"]["aggregation_outputs"]["kebele"]

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---------------- KEBELE JOIN ----------------
    print("▶ Joining kebele-level attributes")

    kebele_gdf = join_kebele_attributes(
        kebele_geojson_path=geojson_path,
        kebele_aggregated_csv=kebele_csv
    )

    kebele_out = output_dir / "kebele_ai_adoption.geojson"
    kebele_gdf.to_file(kebele_out, driver="GeoJSON")
    print(f"✔ Saved {kebele_out}")

    # ---------------- DISSOLVE: WOREDA ----------------
    print("▶ Dissolving to woreda level")

    woreda_gdf = dissolve_level(
        gdf=kebele_gdf,
        level_name="woreda",
        rules=dissolve_rules
    )

    woreda_out = output_dir / "woreda_ai_adoption.geojson"
    woreda_gdf.to_file(woreda_out, driver="GeoJSON")
    print(f"✔ Saved {woreda_out}")

    # ---------------- DISSOLVE: ZONE ----------------
    print("▶ Dissolving to zone level")

    zone_gdf = dissolve_level(
        gdf=woreda_gdf,
        level_name="zone",
        rules=dissolve_rules
    )

    zone_out = output_dir / "zone_ai_adoption.geojson"
    zone_gdf.to_file(zone_out, driver="GeoJSON")
    print(f"✔ Saved {zone_out}")

    # ---------------- DISSOLVE: REGION ----------------
    print("▶ Dissolving to region level")

    region_gdf = dissolve_level(
        gdf=zone_gdf,
        level_name="region",
        rules=dissolve_rules
    )

    region_out = output_dir / "region_ai_adoption.geojson"
    region_gdf.to_file(region_out, driver="GeoJSON")
    print(f"✔ Saved {region_out}")
