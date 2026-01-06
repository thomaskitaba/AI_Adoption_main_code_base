from .pipeline import prepare_ai_ready_dataset


def run_ai_ready_pipeline():
    prepare_ai_ready_dataset(
        geojson_path="data/processed/kebele_ai_adoption.geojson",
        output_csv="data/ai_ready/kebele_ai_features.csv",
        level="kebele"
    )

    prepare_ai_ready_dataset(
        geojson_path="data/processed/woreda_ai_adoption.geojson",
        output_csv="data/ai_ready/woreda_ai_features.csv",
        level="woreda"
    )

    prepare_ai_ready_dataset(
        geojson_path="data/processed/zone_ai_adoption.geojson",
        output_csv="data/ai_ready/zone_ai_features.csv",
        level="zone"
    )

    prepare_ai_ready_dataset(
        geojson_path="data/processed/region_ai_adoption.geojson",
        output_csv="data/ai_ready/region_ai_features.csv",
        level="region"
    )

