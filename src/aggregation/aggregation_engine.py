import pandas as pd
from collections import Counter

def mode(series):
    return Counter(series).most_common(1)[0][0]

def build_agg_dict(rules):
    agg = {}
    for col, rule in rules.items():
        if rule == "mean":
            agg[col] = "mean"
        elif rule == "mode":
            agg[col] = mode
    return agg
