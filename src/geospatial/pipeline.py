# ---------------- Standard library imports ----------------
import yaml                          # For reading YAML configuration files
from pathlib import Path             # For OS-independent path handling

# ---------------- Third-party imports ----------------
import geopandas as gpd              # GeoDataFrame support (geometry + attributes)

# ---------------- Internal pipeline imports ----------------
from .join_engine import join_kebele_attributes   # Joins aggregated indicators to kebele geometry
from .dissolve_engine import dissolve_level       # Dissolves geometry to higher admin levels
from src.validation.spatial_validation import validate_geodataframe  # Spatial validation checks


def run_geospatial_pipeline():
    """
    Runs the full geospatial stage of the pipeline:
    1. Join kebele-level aggregated indicators to geometry
    2. Validate kebele GeoDataFrame
    3. Dissolve geometry to woreda, zone, and region
    4. Validate each dissolved GeoDataFrame
    5. Write GeoJSON outputs
    """

    # ---------------- Load pipeline configuration ----------------
    # Reads global pipeline configuration (paths, run_mode, etc.)
    with open("config/pipeline_config.yaml") as f:
        config = yaml.safe_load(f)

    # Reads dissolve-specific aggregation semantics
    with open("config/dissolve_rules.yaml") as f:
        dissolve_rules = yaml.safe_load(f)

    # ---------------- Select GeoJSON input ----------------
    # Uses small sample GeoJSON for testing if run_mode.use_sample == True
    geojson_path = (
        config["data"]["geojson"]["sample"]
        if config["run_mode"]["use_sample"]
        else config["data"]["geojson"]["full"]
    )

    # ---------------- Select kebele-level aggregated CSV ----------------
    kebele_csv = config["data"]["aggregation_outputs"]["kebele"]

    # ---------------- Prepare output directory ----------------
    # Ensures data/processed exists before writing any GeoJSON
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================================
    # STEP 1: KEBELE-LEVEL GEOSPATIAL JOIN
    # ==========================================================
    print("▶ Joining kebele-level attributes")

    # Join aggregated indicators to kebele geometry
    kebele_gdf = join_kebele_attributes(
        kebele_geojson_path=geojson_path,
        kebele_aggregated_csv=kebele_csv
    )

    # ---- Validate kebele-level GeoDataFrame ----
    validate_geodataframe(kebele_gdf, level="kebele")

    # Write kebele-level GeoJSON to disk
    kebele_out = output_dir / "kebele_ai_adoption.geojson"
    kebele_gdf.to_file(kebele_out, driver="GeoJSON")
    print(f"✔ Saved {kebele_out}")

    # ==========================================================
    # STEP 2: DISSOLVE TO WOREDA LEVEL
    # ==========================================================
    print("▶ Dissolving to woreda level")

    # Dissolve kebele geometry into woreda geometry
    woreda_gdf = dissolve_level(
        gdf=kebele_gdf,               # Input GeoDataFrame (kebele-level)
        level_name="woreda",           # Target administrative level
        rules=dissolve_rules           # YAML-defined aggregation rules
    )

    # ---- Validate woreda-level GeoDataFrame ----
    validate_geodataframe(woreda_gdf, level="woreda")

    # Write woreda-level GeoJSON
    woreda_out = output_dir / "woreda_ai_adoption.geojson"
    woreda_gdf.to_file(woreda_out, driver="GeoJSON")
    print(f"✔ Saved {woreda_out}")

    # ==========================================================
    # STEP 3: DISSOLVE TO ZONE LEVEL
    # ==========================================================
    print("▶ Dissolving to zone level")

    # Dissolve woreda geometry into zone geometry
    zone_gdf = dissolve_level(
        gdf=woreda_gdf,                # Input GeoDataFrame (woreda-level)
        level_name="zone",             # Target administrative level
        rules=dissolve_rules
    )

    # ---- Validate zone-level GeoDataFrame ----
    validate_geodataframe(zone_gdf, level="zone")

    # Write zone-level GeoJSON
    zone_out = output_dir / "zone_ai_adoption.geojson"
    zone_gdf.to_file(zone_out, driver="GeoJSON")
    print(f"✔ Saved {zone_out}")

    # ==========================================================
    # STEP 4: DISSOLVE TO REGION LEVEL
    # ==========================================================
    print("▶ Dissolving to region level")

    # Dissolve zone geometry into region geometry
    region_gdf = dissolve_level(
        gdf=zone_gdf,                  # Input GeoDataFrame (zone-level)
        level_name="region",           # Target administrative level
        rules=dissolve_rules
    )

    # ---- Validate region-level GeoDataFrame ----
    validate_geodataframe(region_gdf, level="region")

    # Write region-level GeoJSON
    region_out = output_dir / "region_ai_adoption.geojson"
    region_gdf.to_file(region_out, driver="GeoJSON")
    print(f"✔ Saved {region_out}")
