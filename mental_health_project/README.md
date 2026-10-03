# Mental Health Self-Check

A full-stack mental health self-assessment web application that combines structured ML models, NLP sentiment analysis, and fuzzy logic inference to produce a holistic wellness score.

## Overview

The app assesses mental wellness across three dimensions:
- **Structured Model**: ML-based prediction from demographic and behavioral features
- **NLP Sentiment**: Text-based sentiment analysis for emotional state detection
- **Fuzzy Logic Engine**: Mamdani fuzzy inference system combining all signals into a final wellness score (0-100)

Two student-specific models are supported:
- **Student Model** (Mumbai University KT Students Dataset) - predicts Has_KT (backlog risk)
- **General Model** (Early Wakeup Health Dataset) - predicts wellness category

## Setup

```bash
pip install -r requirements.txt
python run.py
```

The app runs on `http://localhost:5000`.

## Dataset

Datasets should be placed in `data/raw/`:
- `Mumbai_University_KT_Students_Dataset.csv` - Student academic/wellness data
- `early_wakeup_health_dataset.csv` - General health/wellness survey data
- `Combined Data.csv` - Sentiment analysis training data (statements + labels)

Run notebooks in `notebooks/` (01, 02, 03) in order for EDA and initial model training.

## Pipeline

### Section A (Basic Info)
User provides name, age, gender, occupation. Occupation determines which model path to use (student vs general).

### Section B (Scale Questions)
1-10 scale questions mapped to categories: stress, sleep, mood, anxiety, focus, social, energy, self-worth.

### Section C (Text Questions)
Free-text responses analyzed by NLP sentiment model. Results are aggregated into an NLP score.

### Prediction Flow
```
Section B scores → category_scores (normalized 0-10)
Section C text  → NLP sentiment score (0-1)
User responses  → structured model probability (0-1)

All three inputs → Fuzzy Engine → wellness_score (0-100)
```

## API Endpoints

### GET `/api/mental-health/questions?occupation=student`
Returns dynamically generated questions based on occupation type.

### GET `/api/mental-health/model-columns?occupation=student`
Returns model feature names and importances for the given occupation.

### POST `/api/mental-health/predict`
Main prediction endpoint. Accepts:
```json
{
    "name": "John",
    "age": 21,
    "occupation": "Student",
    "responses": {
        "q1": 5,
        "q2": 3,
        "gender": "Male"
    }
}
```
Returns: `score`, `category`, `strengths`, `areas_to_improve`, `notes`.

### POST `/api/sentiment/analyze`
Analyzes text sentiment. Accepts `{"text": "..."}`. Returns: `sentiment`, `score`, `emotions`.

## Occupation Types

| Occupation Keywords | Model |
|---------------------|-------|
| student, university, college, school | Student (Mumbai University) |
| professional, working, employed, engineer, developer, teacher, doctor | General (Health) |
| (default) | General (Health) |

## Model Architecture

### Structured Models (`models/structured_model_*.pkl`)
- Pipeline: ColumnTransformer (StandardScaler + OneHotEncoder) → RandomForestClassifier
- Student model: 19 features including Age, Stress_Level (categorical), Study_Hours, Attendance, Sleep, Social_Media, SGPA, Commute, Part_Time_Job, etc.
- Health model: Wellness prediction from demographic and behavioral features

### Sentiment Model (`models/` + NLP pipeline)
- TF-IDF vectorizer with n-gram analysis → MultinomialNB classifier
- Labels: Normal, Positive, Happy, Sad, Negative, Stress, Depression, Anxiety, Anger, Fear

### Fuzzy Logic (`fuzzy_logic/`)
- **membership_functions.py**: Triangular membership functions for categories (low/medium/high) and wellness
- **rules.py**: 15 IF-THEN rules combining stress, sleep, mood, anxiety, social, energy, focus, and NLP inputs
- **fuzzy_engine.py**: Runs fuzzification, rule evaluation, and defuzzification (centroid method)

## Key Components

### `app/api.py`
Flask Blueprint with all REST API endpoints. Contains:
- `CATEGORY_MAP`: Maps question categories to wellness dimensions
- `predict_student_structured()`: Loads student model and maps user responses to model features
- `predict()`: Main prediction endpoint combining structured + sentiment + fuzzy outputs
- `sentiment()`: Sentiment analysis endpoint

### `app/question_generator.py`
Dynamically generates questions based on occupation type. Supports:
- `load_questions(occupation)`: Returns question templates
- `load_model_features(occupation)`: Returns model metadata
- `generate_questions_from_columns(occupation)`: Fallback question generation from dataset columns

### `app/routes.py`
Page flow: Section A → B → C → Result. Handles session state and renders templates.

### `app/utils/`
- `predict_structured.py`: General structured model prediction
- `predict_sentiment.py`: NLP sentiment model prediction (transformers fallback)
- `preprocess.py`: Text cleaning and preprocessing
- `aggregate_scores.py`: Aggregates multiple sentiment results into a single score

## File Structure

```
mental_health_project/
├── app/                    # Flask application
│   ├── api.py             # REST API endpoints
│   ├── routes.py          # Page routing and session management
│   ├── question_generator.py  # Dynamic question generation
│   ├── forms.py           # WTForms definitions (optional)
│   ├── __init__.py        # App factory
│   ├── utils/             # Prediction and preprocessing utilities
│   ├── templates/         # HTML templates
│   └── static/            # CSS and JS assets
├── fuzzy_logic/           # Mamdani fuzzy inference system
├── models/                # Trained models (.pkl) and vectorizers
├── data/raw/              # Raw dataset CSVs
├── data/processed/        # Cleaned/encoded data
├── notebooks/             # Jupyter notebooks for EDA
├── train_models.py        # Model training pipeline
├── run.py                 # App entry point
├── config.py              # Flask configuration
└── requirements.txt       # Python dependencies
```

## Wellness Score Categories

| Score Range | Category |
|-------------|----------|
| 75-100 | Excellent |
| 55-74 | Good |
| 35-54 | Moderate |
| 0-34 | Needs Attention |

## Risk Levels (from Fuzzy Engine)

| Score Range | Risk Level |
|-------------|------------|
| ≥ 60 | Low |
| 40-59 | Medium |
| < 40 | High |

## Example Student Prediction

For a student with high stress (q1=9), low study hours (q2=1), poor attendance (q3=50%):

```python
from app.api import predict_student_structured

result = predict_student_structured({
    "q1": 9, "q2": 1, "q3": 50, "q4": 4, "q5": 8,
    "q6": 3.0, "q7": 120, "q8": 2,
    "q9": "Yes", "q10": "No", "q11": "No", "q12": "No",
    "gender": "Female", "branch": "Computer Engineering",
    "year": "Final Year", "commute_mode": "Auto/Cab",
    "financial_status": "Lower Middle Class", "cleared_first_attempt": "No"
})
# Returns probability score based on student model
```

## Development

### Training New Models
Edit `train_models.py` and run:
```bash
python train_models.py
```

### Testing the API
```bash
curl -X POST http://localhost:5000/api/mental-health/predict \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","age":21,"occupation":"student","responses":{"q1":5,"q2":5}}'
```
