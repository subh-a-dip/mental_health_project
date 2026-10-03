import numpy as np
import skfuzzy as fuzz
from fuzzy_logic.membership_functions import get_membership_functions, fuzzify_category
from fuzzy_logic.rules import evaluate_rules


def compute_category_scores(section_b):
    category_scores = {
        "stress": section_b.get("q1", 5),
        "sleep": 11 - section_b.get("q2", 5),
        "self_worth": section_b.get("q9", 5),
        "anxiety": section_b.get("q8", 5),
        "mood": 11 - section_b.get("q6", 5),
        "focus": section_b.get("q4", 5),
        "social": section_b.get("q5", 5),
        "energy": section_b.get("q10", 5),
    }
    return category_scores


def simple_sentiment_score(texts):
    negative_words = ["sad", "depressed", "anxious", "worried", "stressed", "tired", "hopeless", "angry", "fear", "pain", "alone", "lonely", "cry", "crying", "unhappy", "miserable", "terrible", "awful", "bad", "worst"]
    positive_words = ["happy", "good", "great", "wonderful", "excited", "calm", "peaceful", "grateful", "love", "joy", "hope", "better", "fine", "okay", "well", "motivated", "confident", "proud", "blessed", "content"]

    all_text = " ".join(texts).lower()
    neg_count = sum(1 for w in negative_words if w in all_text)
    pos_count = sum(1 for w in positive_words if w in all_text)

    total = neg_count + pos_count
    if total == 0:
        return 0.5

    score = neg_count / total
    return min(max(score, 0), 1)


def run_fuzzy_engine(category_scores, structured_prob, nlp_score):
    mfs = get_membership_functions()
    fuzzified_inputs = {}

    for category, value in category_scores.items():
        if category in mfs:
            fuzzified_inputs[category] = fuzzify_category(value, category, mfs)

    fuzzified_inputs["nlp"] = fuzzify_category(nlp_score * 10, "nlp", mfs)

    aggregated, x_wellness = evaluate_rules(fuzzified_inputs, mfs)

    if aggregated.sum() == 0:
        wellness_score = 50.0
    else:
        wellness_score = fuzz.defuzz(x_wellness, aggregated, "centroid")
        wellness_score = max(0, min(100, float(wellness_score)))

    if wellness_score >= 60:
        risk_level = "Low"
    elif wellness_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "High"

    normalized_breakdown = {}
    for cat, val in category_scores.items():
        normalized_breakdown[cat] = max(0, min(10, val))

    return {
        "wellness_score": round(wellness_score, 1),
        "risk_level": risk_level,
        "category_breakdown": normalized_breakdown,
    }