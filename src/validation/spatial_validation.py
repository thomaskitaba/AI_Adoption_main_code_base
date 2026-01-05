import geopandas as gpd


def validate_geodataframe(
    gdf: gpd.GeoDataFrame,
    level: str
):
    print(f"\n🔎 Validating {level} level")

    # ---- Geometry checks ----
    if gdf.geometry.is_empty.any():
        raise ValueError(f"{level}: Empty geometries detected")

    if not gdf.geometry.is_valid.all():
        raise ValueError(f"{level}: Invalid geometries detected")

    print("✔ Geometry valid")

    # ---- Hierarchy uniqueness ----
    hierarchy_cols = {
        "kebele": ["region", "zone", "woreda", "kebele"],
        "woreda": ["region", "zone", "woreda"],
        "zone": ["region", "zone"],
        "region": ["region"],
    }

    cols = hierarchy_cols[level]
    duplicates = gdf.duplicated(subset=cols)
    if duplicates.any():
        raise ValueError(f"{level}: Duplicate admin units found")

    print("✔ Hierarchy unique")

    # ---- Weight checks ----
    if "num_farmers" in gdf.columns:
        if (gdf["num_farmers"] < 0).any():
            raise ValueError(f"{level}: Negative num_farmers found")
        print("✔ Farmer counts valid")

    # ---- Adoption bounds ----
    adoption_cols = [c for c in gdf.columns if "adoption" in c]

    for col in adoption_cols:
        if ((gdf[col] < 0) | (gdf[col] > 1)).any():
            raise ValueError(f"{level}: Adoption rate out of bounds in {col}")

    print("✔ Adoption rates within [0,1]")

    # ---- CRS check ----
    if gdf.crs is None:
        raise ValueError(f"{level}: CRS missing")

    print(f"✔ CRS OK ({gdf.crs})")
