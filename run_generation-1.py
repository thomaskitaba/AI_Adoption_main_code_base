from src.data_generation.generate_farmers import generate_farmers

OUTPUT_PATH = "data/interim/farmers_synthetic.csv"
# KEBELE_GEOJSON = "data/raw/geo/Ethiopia_AdminBoundaries_No_SNNPR.geojson"
KEBELE_GEOJSON = "data/raw/geo/Ethiopia_Admin_boundaries_smaple.geojson"

df = generate_farmers(KEBELE_GEOJSON)
df.to_csv(OUTPUT_PATH, index=False)

print(f"✔ Farmer-level dataset created: {OUTPUT_PATH}")
print(f"Rows: {len(df)}")





