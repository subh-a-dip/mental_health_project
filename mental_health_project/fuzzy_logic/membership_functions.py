import numpy as np
import skfuzzy as fuzz


def get_membership_functions():
    x = np.arange(0, 11, 1)
    x_wellness = np.arange(0, 101, 1)

    mood = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    stress = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    sleep = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    anxiety = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    self_worth = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    social = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    energy = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    focus = {
        "low": fuzz.trimf(x, [0, 0, 5]),
        "medium": fuzz.trimf(x, [3, 5, 7]),
        "high": fuzz.trimf(x, [5, 10, 10]),
    }

    nlp = {
        "normal": fuzz.trimf(x, [0, 0, 4]),
        "moderate": fuzz.trimf(x, [3, 5, 7]),
        "severe": fuzz.trimf(x, [6, 10, 10]),
    }

    wellness = {
        "low": fuzz.trimf(x_wellness, [0, 0, 40]),
        "medium": fuzz.trimf(x_wellness, [30, 50, 70]),
        "high": fuzz.trimf(x_wellness, [60, 100, 100]),
    }

    return {
        "mood": (x, mood),
        "stress": (x, stress),
        "sleep": (x, sleep),
        "anxiety": (x, anxiety),
        "self_worth": (x, self_worth),
        "social": (x, social),
        "energy": (x, energy),
        "focus": (x, focus),
        "nlp": (x, nlp),
        "wellness": (x_wellness, wellness),
    }


def fuzzify_category(value, category, mfs):
    x, sets = mfs[category]
    result = {}
    for name, mf in sets.items():
        result[name] = fuzz.interp_membership(x, mf, value)
    return result
