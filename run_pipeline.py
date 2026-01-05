#!/usr/bin/python3
import sys
from src.data_generation.pipeline import run_generation_pipeline
from src.aggregation.pipeline import run_aggregation_pipeline
from src.geospatial.pipeline import run_geospatial_pipeline

def main(stage):
    print(f"Running pipeline stage: {stage}")
    if stage == "generate":
        run_generation_pipeline()
    elif stage == "aggregate":
        run_aggregation_pipeline()
    elif stage == "all":
        run_generation_pipeline()
        run_aggregation_pipeline()
    elif stage == "geospatial":
        run_geospatial_pipeline()

    elif stage == "all":
        run_generation_pipeline()
        run_aggregation_pipeline()
        run_geospatial_pipeline()
    else:
        raise ValueError(
            "Usage: python run_pipeline.py [generate|aggregate|all]"
        )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        main("all")
    else:
        main(sys.argv[1])
