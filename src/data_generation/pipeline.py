import yaml
from pathlib import Path
from .generate_farmers import generate_farmers
from pathlib import Path

def run_generation_pipeline():
   

    config_path = Path(__file__).resolve().parents[2] / "config/pipeline_config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)


    geojson_path = (
        config["data"]["geojson"]["sample"]
        if config["run_mode"]["use_sample"]
        else config["data"]["geojson"]["full"]
    )

    output_path = (
        config["data"]["farmer_output_sample"]
        if config["run_mode"]["use_sample"]
        else config["data"]["farmer_output_full"]
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    df = generate_farmers(geojson_path)
    df.to_csv(output_path, index=False)

    print(f"✔ GeoJSON used: {geojson_path}")
    print(f"✔ Farmer data written to: {output_path}")
    print(f"✔ Rows generated: {len(df)}")
