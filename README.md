========================================================================================
  
             DATASET PIPELINE
Raw Data Discovery
→ Administrative Boundary Acquisition (Kebele GeoJSON)
→ Geospatial Cleaning & Harmonization (Remove SNNPR)
→ Literature-Based Feature Discovery (AgTechAdoption.xlsx)
→ Feature Selection & AI Variable Mapping
→ Synthetic Farmer-Level Data Generation (Logit-based)
→ Aggregation Rules Definition
→ Memory-Safe Aggregation (Region → Zone → Woreda → Kebele)
→ ⏭️ Geospatial Join (NEXT)
→ Cleaning & Validation
→ AI-Ready Dataset
→ Visualization & Policy Simulation


***Pipeline Commands:

python run_pipeline.py <stage>
<stage> can be either on of these   generate, aggregate, or all

1. generate syntethic farmer-level data: 
------ python run_pipeline.py generate
What this does:
---Reads kebele-level GeoJSON (sample or full, based on config)
---Generates realistic synthetic farmers
---Applies logit-based AI adoption modeling
---Writes farmer-level CSV to data/interim/

2. Aggregate farmer-level data (memory-safe)

     python run_pipeline.py aggregate

What this does:
---Loads farmer-level CSV in chunks
---Aggregates data region by region
---Produces aggregated datasets at:
------Kebele
------Woreda
------Zone
------Region
------Writes results to data/interim/

3. perform generation and aggrigatino at the sametime

    python run_pipeline.py all

4. Geo spatial join

python run_pipeline.py geospatial

Geospatial Join

After aggregation, the data exists only as tabular CSVs.
This stage:

what it does:
---Re-attaches indicators to spatial boundaries
---Preserves correct administrative hierarchy
---Enables mapping in QGIS, Kepler.gl, GeoPandas
---Prepares datasets for spatial policy simulation




***Switching Between Sample and Full Data

To safely test the pipeline on smaller data:
Edit one line only in:    config/pipeline_config.yaml

run_mode:use_sample:true             # true = small GeoJSON, false = full GeoJSON




========================================================================================


AI Adoption Pipeline Flow (Execution Logic)
Below is the exact execution flow of the pipeline.

1. Entry Point: run_pipeline.py
run_pipeline.py
   │
   ├─ main(sys.argv[1])
   │     │
   │     ├─ if stage == "generate"
   │     │       └─ run_generation_pipeline()
   │     │
   │     ├─ if stage == "aggregate"
   │     │       └─ run_aggregation_pipeline()
   │     │
   │     ├─ if stage == "geospatial"
   │     │       └─ run_geospatial_pipeline()
   │     │
   │     └─ if stage == "all"
   │             ├─ run_generation_pipeline()
   │             ├─ run_aggregation_pipeline()
   │             └─ run_geospatial_pipeline()


2. Synthetic Data Generation flow

src/data_generation/pipeline.py
   │
   ├─ run_generation_pipeline()
   │     │
   │     ├─ reads config/pipeline_config.yaml
   │     │      │
   │     │      └─ selects:
   │     │           • kebele GeoJSON path
   │     │           • output CSV path
   │     │
   │     ├─ ensures output directory exists
   │     │
   │     └─ df = generate_farmers(geojson_path)

src/data_generation/generate_farmers.py
   │
   ├─ generate_farmers(kebele_geojson_path)
   │     │
   │     ├─ reads kebele GeoJSON using geopandas
   │     │
   │     ├─ standardizes admin column names
   │     │
   │     ├─ iterates over kebeles
   │     │
   │     ├─ generates N farmers per kebele
   │     │
   │     ├─ assigns demographic, farm, access variables
   │     │
   │     ├─ computes adoption probability using:
   │     │       └─ adoption_probability() (logit model)
   │     │
   │     └─ samples binary adoption outcomes (0/1)
   │
   └─ returns pd.DataFrame(farmers)
          │
          └─ written to:
                 data/interim/farmers_synthetic.csv



3. Memory Safe Aggregation flow

run_pipeline.py
   │
   └─ run_aggregation_pipeline()

src/aggregation/pipeline.py
   │
   ├─ run_aggregation_pipeline()
   │     │
   │     ├─ reads pipeline_config.yaml
   │     │
   │     ├─ selects farmer-level CSV
   │     │
   │     ├─ reads chunk size and output paths
   │     │
   │     └─ calls:
   │           run_aggregation_memory_safe()


src/aggregation/run_aggregation_memory_safe.py
   │
   ├─ run_aggregation_memory_safe(input_path, outputs, chunk_size)
   │     │
   │     ├─ reads aggregation_rules.yaml
   │     │
   │     ├─ builds aggregation dictionary
   │     │
   │     ├─ identifies unique regions
   │     │
   │     ├─ processes one region at a time
   │     │
   │     ├─ reads farmer CSV in chunks
   │     │
   │     │
   │     ├─ aggregates at:
   │     │       • kebele
   │     │       • woreda
   │     │       • zone
   │     │       • region
   │     │
   │     └─ writes CSVs to:
   │             data/interim/kebele_aggregated.csv
   │             data/interim/woreda_aggregated.csv
   │             data/interim/zone_aggregated.csv
   │             data/interim/region_aggregated.csv


4. Geo spatial join and map ready output

    4.1  geo spatioal pipeline orchastration
        src/geospatial/pipeline.py
        │
        ├─ run_geospatial_pipeline()
        │     │
        │     ├─ reads pipeline_config.yaml
        │     │
        │     ├─ selects:
        │     │      • kebele boundary GeoJSON
        │     │      • kebele_aggregated.csv
        │     │      • output GeoJSON path
        │     │
        │     └─ calls:
        │           join_kebele_attributes()

    4. 2: core join logic

        src/geospatial/join_engine.py
        │
        ├─ join_kebele_attributes(
        │        kebele_geojson_path,
        │        kebele_aggregated_csv,
        │        join_key="kebele_id"
        │     )
        │
        │     ├─ loads kebele boundaries with geopandas
        │     ├─ loads aggregated adoption CSV
        │     ├─ validates join keys
        │     ├─ performs left spatial-attribute join
        │     ├─ preserves geometry
        │     └─ returns GeoDataFrame

4.3 Final Processed output 

    GeoDataFrame
    │
    └─ written to:
            data/processed/kebele_ai_adoption.geojson
# AI_Adoption_main_code_base






5. Dissolve: 

Geometry Dissolve means:  mergin keble level polygons to form woreds. based on shared attributes while combininig their data correctly.


Kebele GeoJSON
   + aggregated indicators
          │
          ▼
Kebele AI Adoption GeoJSON  (already done)
          │
          ▼
DISSOLVE BY ["region","zone","woreda"]
          │
          ▼
Woreda AI Adoption GeoJSON
          │
          ▼
DISSOLVE BY ["region","zone"]
          │
          ▼
Zone AI Adoption GeoJSON
          │
          ▼
DISSOLVE BY ["region"]
          │
          ▼
Region AI Adoption GeoJSON



6. 
Note: CRS stands for Coordinate Reference System.
Common Standards to be used:
The text mentions EPSG:4326. This is the most common coordinate system in the world (used by GPS and Google Earth). It uses latitude and longitude to represent locations on a spherical model of the Earth (WGS84).


