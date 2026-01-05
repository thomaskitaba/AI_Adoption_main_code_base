import numpy as np

def logistic(x):
    return 1 / (1 + np.exp(-x))

def education_score(level):
    return {
        "None": 0.0,
        "Primary": 0.8,
        "Secondary": 1.5,
        "Diploma+": 2.2
    }[level]

def adoption_probability(row):
    score = 0
    score += education_score(row["farmer_education_level"])
    score += 0.6 * row["extension_access"]
    score += 0.5 * row["credit_access"]
    score -= 0.07 * row["distance_to_market_km"]
    score += 0.8 * (row["ai_awareness_level"] == "High")
    return logistic(score)
