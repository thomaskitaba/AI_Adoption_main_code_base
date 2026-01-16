# src/visualization/loader.py

import json
from pathlib import Path
from functools import lru_cache
from .utils import get_diverging_color

# Base directory where policy map GeoJSONs are stored
DATA_DIR = Path("data/policy_maps")


@lru_cache(maxsize=32)
def load_geojson(scenario: str, level: str):
    """
    Load and cache a GeoJSON file for a given policy scenario and admin level.

    Parameters
    ----------
    scenario : str
        Policy scenario name (e.g., 'credit_reform')
    level : str
        Administrative level ('woreda', 'zone', 'region')

    Returns
    -------
    dict
        GeoJSON FeatureCollection as a Python dict
    """

    # Construct filename using pipeline naming convention
    path = DATA_DIR / f"{scenario}_{level}.geojson"

    # Fail gracefully if file does not exist
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON not found: {path}")

    # Read GeoJSON from disk
    with open(path, "r") as f:
        geojson = json.load(f)

    # Add fillColor to each feature's properties
    for feature in geojson["features"]:
        pe = feature["properties"].get("policy_effect", 0.0)
        feature["properties"]["fillColor"] = get_diverging_color(pe)

    return geojson
