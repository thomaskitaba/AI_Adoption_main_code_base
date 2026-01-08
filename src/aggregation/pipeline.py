import yaml
from .run_aggregation_memory_safe import run_aggregation_memory_safe

def run_aggregation_pipeline():
    with open("config/pipeline_config.yaml") as f:
        config = yaml.safe_load(f)

    input_path = (
        config["data"]["farmer_output_sample"]
        if config["run_mode"]["use_sample"]
        else config["data"]["farmer_output_full"]
    )

    outputs = config["data"]["aggregation_outputs"]
    chunk_size = config["aggregation"]["chunk_size"]

    run_aggregation_memory_safe(
        input_path=input_path,
        outputs=outputs,
        chunk_size=chunk_size
    )
    #
