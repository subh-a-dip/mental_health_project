import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def train_student_model():
    print("=== Training Student (Mumbai University) Model ===")
    df = pd.read_csv(os.path.join(DATA_DIR, "Mumbai_University_KT_Students_Dataset.csv"))

    target = "Has_KT"
    y = df[target].map({"Yes": 1, "No": 0})
    X = df.drop(columns=["Student_ID", target])

    num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object"]).columns.tolist()

    num_cols = [c for c in num_cols if c not in ["Number_of_KTs"]]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=["No KT", "Has KT"]))

    path = os.path.join(MODELS_DIR, "structured_model_student.pkl")
    joblib.dump(model, path)
    print(f"Saved: {path}")

    print(f"\nModel features ({len(num_cols) + len(cat_cols)}):")
    print(f"  Numeric: {num_cols}")
    print(f"  Categorical: {cat_cols}")

    return model, num_cols, cat_cols


def train_health_model():
    print("\n=== Training Health (Early Wakeup) Model ===")
    df = pd.read_csv(os.path.join(DATA_DIR, "early_wakeup_health_dataset.csv"))

    target = "Wellness_Category"
    y = df[target]
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    X = df.drop(columns=["Person_ID", "Wellness_Category", "Early_Waker", "Fitness_Level", "Healthy_Aging_Score"])

    num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("scaler", StandardScaler())]), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    path = os.path.join(MODELS_DIR, "structured_model_health.pkl")
    joblib.dump(model, path)
    print(f"Saved: {path}")

    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder_health.pkl"))
    print(f"Saved label encoder")

    print(f"\nModel features ({len(num_cols) + len(cat_cols)}):")
    print(f"  Numeric: {num_cols}")
    print(f"  Categorical: {cat_cols}")

    return model, num_cols, cat_cols, le


def train_sentiment_model():
    print("\n=== Training Sentiment Model ===")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB

    df = pd.read_csv(os.path.join(DATA_DIR, "Combined Data.csv"))
    df = df.dropna(subset=["statement", "status"])

    target = "status"
    y = df[target]
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    X = df["statement"]

    model = Pipeline([
        ("tfidf", TfidfVectorizer(max_df=0.95, max_features=5000, min_df=2, ngram_range=(1, 2), stop_words="english")),
        ("classifier", MultinomialNB(alpha=0.1)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    path = os.path.join(MODELS_DIR, "structured_model_sentiment.pkl")
    joblib.dump(model, path)
    print(f"Saved: {path}")

    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder_sentiment.pkl"))
    print(f"Saved label encoder")

    return model, le


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)

    train_student_model()
    train_health_model()
    train_sentiment_model()

    print("\n=== All models trained successfully! ===")
