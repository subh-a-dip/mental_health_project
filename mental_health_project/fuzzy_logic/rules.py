import numpy as np

RULES = [
    {"conditions": {"stress": "high", "sleep": "low", "nlp": "severe"}, "conclusion": "low"},
    {"conditions": {"stress": "high", "anxiety": "high"}, "conclusion": "low"},
    {"conditions": {"mood": "low", "self_worth": "low"}, "conclusion": "low"},
    {"conditions": {"energy": "low", "sleep": "low"}, "conclusion": "low"},
    {"conditions": {"social": "low", "mood": "low"}, "conclusion": "low"},
    {"conditions": {"focus": "low", "stress": "high"}, "conclusion": "low"},
    {"conditions": {"stress": "medium", "sleep": "low"}, "conclusion": "medium"},
    {"conditions": {"anxiety": "medium", "mood": "medium"}, "conclusion": "medium"},
    {"conditions": {"self_worth": "medium", "social": "medium"}, "conclusion": "medium"},
    {"conditions": {"energy": "medium", "focus": "medium"}, "conclusion": "medium"},
    {"conditions": {"mood": "high", "sleep": "high", "social": "high"}, "conclusion": "high"},
    {"conditions": {"stress": "low", "energy": "high"}, "conclusion": "high"},
    {"conditions": {"self_worth": "high", "focus": "high"}, "conclusion": "high"},
    {"conditions": {"nlp": "normal", "stress": "low"}, "conclusion": "high"},
    {"conditions": {"sleep": "high", "anxiety": "low"}, "conclusion": "high"},
]


def evaluate_rules(fuzzified_inputs, mfs):
    x_wellness, wellness_sets = mfs["wellness"]

    aggregated = np.zeros_like(x_wellness, dtype=float)

    for rule in RULES:
        antecedent_strength = 1.0
        for var, level in rule["conditions"].items():
            if var in fuzzified_inputs:
                antecedent_strength = min(antecedent_strength, fuzzified_inputs[var].get(level, 0))
            elif var == "nlp" and "nlp" in fuzzified_inputs:
                antecedent_strength = min(antecedent_strength, fuzzified_inputs["nlp"].get(level, 0))

        if antecedent_strength > 0:
            conclusion_level = rule["conclusion"]
            mf = wellness_sets[conclusion_level]
            clipped = np.minimum(mf, antecedent_strength)
            aggregated = np.maximum(aggregated, clipped)

    return aggregated, x_wellness