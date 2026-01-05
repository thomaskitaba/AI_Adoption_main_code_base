import numpy as np
import pandas as pd
import geopandas as gpd

from .adoption_model import adoption_probability
from .utils import bounded_normal, categorical

np.random.seed(42)

def generate_farmers(kebele_geojson_path):
    kebeles = gpd.read_file(kebele_geojson_path)

    # standardize column names
    kebeles = kebeles.rename(columns={
    'R_NAME': 'region',
    'Z_NAME': 'zone',
    'W_NAME': 'woreda',
    'KK_NAME': 'kebele'
})

    # Ensure kebele is populated — fallback to other name fields or synthesize
    kebeles['kebele'] = kebeles.get('kebele', '').fillna('').astype(str).str.strip()
    for alt in ['T_NAME', 'UK_NAME', 'RK_NAME']:
        if alt in kebeles.columns:
            mask = kebeles['kebele'] == ''
            if mask.any():
                kebeles.loc[mask, 'kebele'] = kebeles.loc[mask, alt].fillna('').astype(str).str.strip()

    # For any remaining empty kebeles, synthesize a unique identifier using woreda and index
    mask = kebeles['kebele'].astype(str).str.strip() == ''
    if mask.any():
        kebeles.loc[mask, 'kebele'] = kebeles.loc[mask].apply(
            lambda r: f"{r['woreda']}_unk_{r.name}", axis=1
        )

    farmers = []
    print(kebeles.head())
    print(kebeles.columns)

    for _, k in kebeles.iterrows():
        n = np.random.randint(80, 150)

        for i in range(n):
            age = int(bounded_normal(45, 12, 18, 80))

            farmer = {
                # ---- IDENTIFICATION ----
                "study_id": f"{k['kebele']}_{i}",
                "source_reference": "Synthetic_AgTechAdoption",
                "country": "Ethiopia",

                # ---- AI TECHNOLOGY ----
                "ai_technology_type": categorical(
                    ["Crop AI", "Livestock AI", "Integrated AI"],
                    [0.4, 0.3, 0.3]
                ),
                "ai_category": categorical(
                    ["IV", "NRM", "Package"],
                    [0.4, 0.4, 0.2]
                ),
                "ai_feedback_speed": categorical(
                    ["Short", "Medium", "Long"],
                    [0.4, 0.4, 0.2]
                ),
                "ai_trial_available": np.random.binomial(1, 0.5),
                "ai_labor_saving": np.random.binomial(1, 0.6),

                # ---- LOCATION ----
                "region": k['region'],
                "zone": k['zone'],
                "woreda": k['woreda'],
                "kebele": k['kebele'],

                # ---- DEMOGRAPHICS ----
                "age": age,
                "age_squared": age ** 2,
                "sex": categorical(["Male", "Female"], [0.75, 0.25]),
                "household_size": np.random.randint(2, 9),

                # ---- EDUCATION ----
                "farmer_education_level": categorical(
                    ["None", "Primary", "Secondary", "Diploma+"],
                    [0.45, 0.35, 0.15, 0.05]
                ),
                "ai_awareness_level": categorical(
                    ["Low", "Medium", "High"],
                    [0.4, 0.4, 0.2]
                ),
                "num_degree_holders_household": np.random.choice([0,1,2,3], p=[0.6,0.25,0.1,0.05]),

                # ---- FARM ----
                "farming_experience_years": max(age - 15, 1),
                "land_size_ha": round(np.random.lognormal(0.6, 0.6), 2),
                "soil_fertility_status": categorical(
                    ["Poor", "Moderate", "Fertile"],
                    [0.3, 0.4, 0.3]
                ),
                "land_slope_category": categorical(
                    ["Flat", "Gentle", "Steep"],
                    [0.4, 0.4, 0.2]
                ),

                # ---- ACCESS ----
                "distance_to_market_km": round(np.random.exponential(6), 1),
                "travel_time_to_extension": round(np.random.exponential(1.5), 1),
                "credit_access": np.random.binomial(1, 0.45),
                "financial_constraint": np.random.binomial(1, 0.4),
                "land_tenure_security": np.random.binomial(1, 0.7),
                "livestock_ownership": categorical(
                    ["None", "Low", "Medium", "High"],
                    [0.2, 0.4, 0.25, 0.15]
                ),
                "non_farm_income": np.random.binomial(1, 0.35),
                "extension_access": np.random.binomial(1, 0.55),
                "extension_contact_frequency": categorical(
                    ["None", "Rare", "Occasional", "Frequent"],
                    [0.3, 0.3, 0.25, 0.15]
                ),
                "farmer_group_membership": np.random.binomial(1, 0.4),
            }

            # ---- ADOPTION ----
            p = adoption_probability(farmer)
            farmer["ai_crop_advisory_adoption"] = np.random.binomial(1, p)
            farmer["ai_livestock_advisory_adoption"] = np.random.binomial(1, p * 0.8)
            farmer["ai_driven_technology_adoption"] = int(
                farmer["ai_crop_advisory_adoption"] or
                farmer["ai_livestock_advisory_adoption"]
            )

            farmers.append(farmer)

    return pd.DataFrame(farmers)
