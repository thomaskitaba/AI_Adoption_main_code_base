#!/usr/bin/python3
import sys
from src.data_generation.pipeline import run_generation_pipeline
from src.aggregation.pipeline import run_aggregation_pipeline
from src.geospatial.pipeline import run_geospatial_pipeline
from src.ai_ready.run import run_ai_ready_pipeline
from src.modeling.run import run_modeling_pipeline
from src.modeling.policy_simulation import run_policy_simulation
from src.policy_mapping.pipeline import run_policy_mapping
from src.modeling.policy_analysis import run_policy_analysis
from src.policy_analysis.pipeline import run_policy_comparison
from src.policy_equity.pipeline import run_policy_equity




def main(stage):
    print(f"Running pipeline stage: {stage}")
    if stage == "generate":
        run_generation_pipeline()
    elif stage == "aggregate":
        run_aggregation_pipeline()

    elif stage == "geospatial":
        run_geospatial_pipeline()

    elif stage == "ai_ready":
        run_ai_ready_pipeline()

    elif stage == "model":
        run_modeling_pipeline()
    
    elif stage == "policy":
        run_policy_simulation()
    elif stage == "policy_analysis":
        run_policy_analysis()
    elif stage == "policy_map":
        run_policy_mapping()
    elif stage == "policy_comparison":
        run_policy_comparison()
    elif stage == "policy_equity":
        run_policy_equity()
    


    elif stage == "all":
        run_generation_pipeline()
        run_aggregation_pipeline()
        run_geospatial_pipeline()
        run_ai_ready_pipeline()
        run_modeling_pipeline()
        run_policy_simulation()
        run_policy_mapping()
        run_policy_analysis()
        run_policy_comparison()
        run_policy_equity()

    else:
        raise ValueError(
            "Usage: python run_pipeline.py [generate|aggregate|all|geospatial|ai_ready|model|policy|policy_map|policy_analysis|policy_comparison|policy_equity]"
        )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        main("all")
    else:
        main(sys.argv[1])
