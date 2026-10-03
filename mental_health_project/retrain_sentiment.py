"""
Retrain the 7-class sentiment / mental-health statement classifier.

Improvements over the original notebook pipeline:
- Deduplicates statements and drops nulls BEFORE splitting. The original notebook
  dropped nulls only after deriving text_length, and never removed the 1969 duplicate
  statements, so identical text could sit on both sides of the split.
- Stratified 70:30 split.
- Word (1,2)-gram TF-IDF UNION char_wb (3,4)-gram TF-IDF, so short user sentences
  ("i am very happy") and long clinical posts both get usable features.
- Vectorizers are fit ONCE and shared by every candidate classifier. The original
  rebuilt the full vectorizer per model inside a Pipeline.
- Selection by macro F1. The original ranked by weighted F1, which is dominated by
  Normal (31%) and Depression (30%) and largely ignores the five small classes.
- class_weight="balanced" where supported, to counter the 31% vs 1.8% imbalance.

Saves: models/structured_model_sentiment.pkl  (Pipeline: features -> classifier)
       models/label_encoder_sentiment.pkl     (LabelEncoder)
"""

import functools
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

from app.utils.text_cleaning import clean_text

RANDOM_STATE = 42
TEST_SIZE = 0.30
MAX_CHARS = 2000

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "data", "raw", "Combined Data.csv")
MODELS_DIR = os.path.join(ROOT, "models")

np.random.seed(RANDOM_STATE)


def log(*args):
    print(*args, flush=True)


def load_dataset():
    df = pd.read_csv(DATA_PATH)
    log("Raw shape:", df.shape)

    before = len(df)
    df = df.dropna(subset=["statement"])
    df["statement"] = df["statement"].astype(str)
    df = df[df["statement"].str.strip().str.len() > 0]
    log(f"After dropping null/empty: {len(df)} (removed {before - len(df)})")

    before = len(df)
    df = df.drop_duplicates(subset=["statement"], keep="first")
    log(f"After dedup: {len(df)} (removed {before - len(df)})")

    df["cleaned"] = df["statement"].apply(clean_text)
    df = df[df["cleaned"].str.len() > 0]

    # Char n-grams cost scales with total characters, and the longest documents
    # (some 30k+ chars) dominate that cost without changing their label.
    df["cleaned"] = df["cleaned"].str.slice(0, MAX_CHARS)
    df = df[df["cleaned"].str.len() > 0]
    log(f"After {MAX_CHARS}-char cap: {len(df)}")

    return df.reset_index(drop=True)


def build_vectorizer():
    word_tfidf = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        max_features=60000,
        stop_words="english",
        sublinear_tf=True,
        min_df=2,
        lowercase=True,
    )
    char_tfidf = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 4),
        max_features=60000,
        sublinear_tf=True,
        min_df=3,
        lowercase=True,
    )
    return FeatureUnion([("word", word_tfidf), ("char", char_tfidf)])


def candidate_models():
    models = {
        "LogisticRegression_balanced": LogisticRegression(
            max_iter=3000, C=2.0, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "LogisticRegression_C10": LogisticRegression(
            max_iter=3000, C=10.0, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "ComplementNB": ComplementNB(alpha=0.3),
        "SGD_modified_huber": SGDClassifier(
            loss="modified_huber",
            alpha=1e-5,
            max_iter=3000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "LinearSVC": LinearSVC(C=0.5, class_weight="balanced", random_state=RANDOM_STATE),
    }

    try:
        from xgboost import XGBClassifier

        models["XGBoost"] = XGBClassifier(
            n_estimators=250,
            learning_rate=0.2,
            max_depth=8,
            min_child_weight=2,
            subsample=0.85,
            colsample_bytree=0.6,
            reg_lambda=1.0,
            objective="multi:softprob",
            eval_metric="mlogloss",
            n_jobs=-1,
            random_state=RANDOM_STATE,
            tree_method="hist",
        )
    except ImportError:
        log("XGBoost not available, skipping")

    return models


def wrap_for_probability(model, name):
    """LinearSVC has no predict_proba; the API needs it to report confidence."""
    if name == "LinearSVC":
        return CalibratedClassifierCV(model, cv=3, method="sigmoid")
    return model


def main():
    df = load_dataset()

    log("\nClass distribution after cleaning:")
    log(df["status"].value_counts().to_string())
    log()
    log(df["status"].value_counts(normalize=True).round(4).to_string())

    label_encoder = LabelEncoder()
    df["target"] = label_encoder.fit_transform(df["status"])
    log("\nLabel mapping:")
    for i, label in enumerate(label_encoder.classes_):
        log(f"  {i}: {label}")

    X = df["cleaned"]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    log(f"\nTrain: {len(X_train)}  Test: {len(X_test)}")

    log("\nFitting vectorizers once (shared by all candidates)...")
    started = time.time()
    vectorizer = build_vectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    log(f"  train matrix: {X_train_tfidf.shape}  test matrix: {X_test_tfidf.shape}")
    log(f"  vectorizer fit took {time.time() - started:.1f}s")

    results = []
    best_name = None
    best_f1 = -1.0
    best_classifier = None

    for name, model in candidate_models().items():
        log("")
        log("=" * 60)
        log(f"Training {name}")
        log("=" * 60)
        classifier = wrap_for_probability(model, name)
        started = time.time()
        try:
            classifier.fit(X_train_tfidf, y_train)
        except Exception as exc:
            log(f"  FAILED: {exc}")
            continue
        fit_seconds = time.time() - started

        y_pred = classifier.predict(X_test_tfidf)
        acc = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average="macro")
        weighted_f1 = f1_score(y_test, y_pred, average="weighted")

        log(f"  Accuracy    : {acc:.4f}")
        log(f"  Macro F1    : {macro_f1:.4f}")
        log(f"  Weighted F1 : {weighted_f1:.4f}")
        log(f"  Fit time    : {fit_seconds:.1f}s")
        log("")
        log(
            classification_report(
                y_test, y_pred, target_names=label_encoder.classes_, zero_division=0
            )
        )

        results.append(
            {
                "model": name,
                "accuracy": acc,
                "macro_f1": macro_f1,
                "weighted_f1": weighted_f1,
                "fit_seconds": round(fit_seconds, 1),
            }
        )

        if macro_f1 > best_f1:
            best_f1 = macro_f1
            best_name = name
            best_classifier = classifier

    if best_classifier is None:
        log("All models failed to train.")
        sys.exit(1)

    results_df = pd.DataFrame(results).sort_values("macro_f1", ascending=False)
    log("")
    log("=" * 60)
    log("MODEL COMPARISON (sorted by macro F1)")
    log("=" * 60)
    log(results_df.to_string(index=False))
    log(f"\nBest model: {best_name} (macro F1 = {best_f1:.4f})")

    pipeline = Pipeline(
        [("features", vectorizer), ("classifier", best_classifier)]
    )

    # Sanity check the serialized pipeline on a few strings before writing.
    for sample in [
        "i am very happy today",
        "i feel hopeless and want to give up",
        "i am so anxious about everything",
    ]:
        pred_index = pipeline.predict([sample])[0]
        log(f"  check {sample!r} -> {label_encoder.inverse_transform([pred_index])[0]}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, "structured_model_sentiment.pkl")
    le_path = os.path.join(MODELS_DIR, "label_encoder_sentiment.pkl")

    joblib.dump(pipeline, model_path)
    joblib.dump(label_encoder, le_path)

    log(f"\nSaved model   : {model_path}")
    log(f"Saved encoder : {le_path}")
    log(f"Split         : {1 - TEST_SIZE:.0%}/{TEST_SIZE:.0%} stratified, seed {RANDOM_STATE}")


if __name__ == "__main__":
    main()
