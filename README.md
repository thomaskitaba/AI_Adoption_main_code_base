========================================================================================
AI ADOPTION DATASET PIPELINE
========================================================================================

This repository implements a **modular, memory-safe, and geospatially consistent**
data pipeline for **AI & agricultural technology adoption analysis**.

The pipeline transforms **raw administrative boundary data and literature-driven
adoption assumptions** into **AI-ready, policy-simulatable datasets** at multiple
administrative levels (Kebele → Woreda → Zone → Region).

----------------------------------------------------------------------------------------
PIPELINE OVERVIEW
----------------------------------------------------------------------------------------

Raw Data Discovery
→ Administrative Boundary Acquisition (Kebele GeoJSON)
→ Geospatial Cleaning & Harmonization (e.g. Remove SNNPR)
→ Literature-Based Feature Discovery (AgTechAdoption.xlsx)
→ Feature Selection & AI Variable Mapping
→ Synthetic Farmer-Level Data Generation (Logit-based)
→ Aggregation Rules Definition
→ Memory-Safe Aggregation (Region → Zone → Woreda → Kebele)
→ Geospatial Join
→ Cleaning & Validation
→ AI-Ready Dataset
→ Visualization & Policy Simulation

----------------------------------------------------------------------------------------
PIPELINE COMMANDS
----------------------------------------------------------------------------------------

The pipeline is executed via a **single orchestration script**:

    python run_pipeline.py <stage>

Where `<stage>` can be one of:

- generate
- aggregate
- geospatial
- all

----------------------------------------
1. Synthetic Farmer-Level Data Generation
----------------------------------------

Command:
    python run_pipeline.py generate

What this does:
- Reads kebele-level GeoJSON (sample or full, based on config)
- Generates realistic synthetic farmers per kebele
- Assigns demographics, farm, access, and institutional variables
- Applies a **logit-based AI adoption probability model**
- Samples binary adoption outcomes (0/1)
- Writes farmer-level CSV to:

    data/interim/farmers_synthetic.csv

----------------------------------------
2. Memory-Safe Aggregation
----------------------------------------

Command:
    python run_pipeline.py aggregate

What this does:
- Loads farmer-level CSV in chunks (no RAM explosion)
- Processes **one region at a time**
- Applies explicit aggregation rules (NO implicit averaging)
- Produces adoption indicators at:
    - Kebele
    - Woreda
    - Zone
    - Region

Outputs:
    data/interim/kebele_aggregated.csv
    data/interim/woreda_aggregated.csv
    data/interim/zone_aggregated.csv
    data/interim/region_aggregated.csv

----------------------------------------
3. Full Pipeline Execution
----------------------------------------

Command:
    python run_pipeline.py all

What this does:
- Runs generation
- Runs aggregation
- Runs geospatial join
- Produces **map-ready GeoJSON outputs**

----------------------------------------
4. Geospatial Join
----------------------------------------

Command:
    python run_pipeline.py geospatial

After aggregation, data exists only as tabular CSVs.
This stage:

What it does:
- Re-attaches aggregated indicators to spatial boundaries
- Preserves administrative hierarchy
- Enables mapping in:
    - QGIS
    - Kepler.gl
    - GeoPandas
- Prepares datasets for spatial policy simulation

Output:
    data/processed/kebele_ai_adoption.geojson

----------------------------------------------------------------------------------------
SWITCHING BETWEEN SAMPLE AND FULL DATA
----------------------------------------------------------------------------------------

To safely test the pipeline on smaller data, edit **one line only**:

File:
    config/pipeline_config.yaml

Change:
    run_mode:
      use_sample: true   # true = small GeoJSON, false = full GeoJSON

----------------------------------------------------------------------------------------
AI ADOPTION PIPELINE FLOW (EXECUTION LOGIC)
----------------------------------------------------------------------------------------

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

----------------------------------------------------------------------------------------
2. Synthetic Data Generation Flow
----------------------------------------------------------------------------------------

src/data_generation/pipeline.py
   │
   ├─ run_generation_pipeline()
   │     │
   │     ├─ reads config/pipeline_config.yaml
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
   │     ├─ reads kebele GeoJSON using GeoPandas
   │     ├─ standardizes admin column names
   │     ├─ iterates over kebeles
   │     ├─ generates N farmers per kebele
   │     ├─ assigns demographic, farm, and access variables
   │     ├─ computes adoption probability using a logit model
   │     └─ samples binary adoption outcomes
   │
   └─ returns pandas.DataFrame
          └─ written to data/interim/farmers_synthetic.csv

----------------------------------------------------------------------------------------
3. Memory-Safe Aggregation Flow
----------------------------------------------------------------------------------------

src/aggregation/pipeline.py
   │
   ├─ run_aggregation_pipeline()
   │     │
   │     ├─ reads pipeline_config.yaml
   │     ├─ selects farmer-level CSV
   │     ├─ reads chunk size and output paths
   │     └─ calls run_aggregation_memory_safe()

src/aggregation/run_aggregation_memory_safe.py
   │
   ├─ run_aggregation_memory_safe(input_path, outputs, chunk_size)
   │     │
   │     ├─ reads aggregation_rules.yaml
   │     ├─ builds explicit aggregation dictionary
   │     ├─ identifies unique regions
   │     ├─ processes one region at a time
   │     ├─ aggregates at kebele, woreda, zone, region
   │     └─ writes CSV outputs to data/interim/

IMPORTANT RULE:
- Adoption rates are **always weighted by number of farmers**
- NO implicit averaging. EVER.

----------------------------------------------------------------------------------------
4. Geospatial Join & Map-Ready Output
----------------------------------------------------------------------------------------

4.1 Pipeline Orchestration

src/geospatial/pipeline.py
   │
   ├─ run_geospatial_pipeline()
   │     │
   │     ├─ reads pipeline_config.yaml
   │     ├─ selects kebele GeoJSON and aggregated CSV
   │     └─ calls join_kebele_attributes()

4.2 Core Join Logic

src/geospatial/join_engine.py
   │
   ├─ join_kebele_attributes(
   │        kebele_geojson_path,
   │        kebele_aggregated_csv,
   │        join_key="kebele_id"
   │     )
   │
   │     ├─ loads boundaries with GeoPandas
   │     ├─ loads aggregated indicators
   │     ├─ validates join keys
   │     ├─ performs left attribute join
   │     ├─ preserves geometry
   │     └─ returns GeoDataFrame

4.3 Final Output

    data/processed/kebele_ai_adoption.geojson

----------------------------------------------------------------------------------------
5. Geometry Dissolve (Administrative Roll-Up)
----------------------------------------------------------------------------------------

Geometry dissolve means **merging lower-level polygons into higher-level units**
based on shared administrative attributes while correctly aggregating indicators.

Kebele AI Adoption GeoJSON
          │
          ▼
DISSOLVE BY ["region", "zone", "woreda"]
          │
          ▼
Woreda AI Adoption GeoJSON
          │
          ▼
DISSOLVE BY ["region", "zone"]
          │
          ▼
Zone AI Adoption GeoJSON
          │
          ▼
DISSOLVE BY ["region"]
          │
          ▼
Region AI Adoption GeoJSON

----------------------------------------------------------------------------------------
6. Coordinate Reference System (CRS)
----------------------------------------------------------------------------------------

CRS = Coordinate Reference System

Standard used:
- EPSG:4326 (WGS84)

Why:
- Global standard
- Used by GPS, Google Maps, Google Earth
- Required for interoperability across GIS tools

All GeoJSON outputs **must remain in EPSG:4326** unless explicitly re-projected.

----------------------------------------------------------------------------------------
PROJECT GOAL
----------------------------------------------------------------------------------------

To produce:
- Scientifically defensible
- Policy-relevant
- AI-ready
- Spatially consistent

datasets for **AI adoption analysis in agriculture**, suitable for:
- Research
- Visualization
- Policy simulation
- Scenario analysis

========================================================================================
AI_Adoption_main_code_base
========================================================================================
