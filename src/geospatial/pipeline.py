import yaml
from pathlib import Path
from .join_engine import join_kebele_attributes
# from .join_engine import kebele_geospatial_join

def run_geospatial_pipeline():
    with open("config/pipeline_config.yaml") as f:
        config = yaml.safe_load(f)

    # Select GeoJSON based on run_mode
    geojson_path = (
        config["data"]["geojson"]["sample"]
        if config["run_mode"]["use_sample"]
        else config["data"]["geojson"]["full"]
    )

    kebele_csv = config["data"]["aggregation_outputs"]["kebele"]
    output_geojson = "data/processed/kebele_ai_adoption.geojson"

    Path(output_geojson).parent.mkdir(parents=True, exist_ok=True)

    gdf = join_kebele_attributes(
        kebele_geojson_path=geojson_path,
        kebele_aggregated_csv=kebele_csv,
        join_key="kebele_id"
    )

    gdf.to_file(output_geojson, driver="GeoJSON")

    print(f"✔ GeoJSON used: {geojson_path}")
    print(f"✔ Aggregated CSV used: {kebele_csv}")
    print(f"✔ Output written to: {output_geojson}")
