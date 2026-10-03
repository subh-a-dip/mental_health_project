import json
import os
import pandas as pd
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")

DATASET_QUESTIONS = {
    "student": {
        "dataset": "Mumbai_University_KT_Students_Dataset.csv",
        "model": "structured_model_student.pkl",
        "preprocessor": "preprocessor_mumbai_university.pkl",
        "target": "Has_KT",
        "questions": [
            {"id": "q1", "category": "Stress", "question": "How stressed do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not stressed, 10 = Extremely stressed", "column": "Stress_Level"},
            {"id": "q2", "category": "Study", "question": "How many hours do you study per day?", "type": "number", "minValue": 0, "maxValue": 12, "step": 0.5, "unit": "hours", "description": "Average daily study hours (e.g., 4.5)", "column": "Study_Hours_per_Day"},
            {"id": "q3", "category": "Attendance", "question": "What is your attendance percentage?", "type": "number", "minValue": 0, "maxValue": 100, "unit": "%", "description": "Your current attendance percentage", "column": "Attendance_Percentage"},
            {"id": "q4", "category": "Sleep", "question": "How many hours do you sleep per night?", "type": "number", "minValue": 0, "maxValue": 14, "step": 0.5, "unit": "hours", "description": "Hours per night (e.g., 7.5)", "column": "Sleep_Hours_per_Night"},
            {"id": "q5", "category": "Social Media", "question": "How many hours on social media daily?", "type": "number", "minValue": 0, "maxValue": 12, "step": 0.5, "unit": "hours", "description": "Daily social media hours", "column": "Social_Media_Hours_per_Day"},
            {"id": "q6", "category": "SGPA", "question": "What is your previous semester SGPA?", "type": "number", "minValue": 0, "maxValue": 10, "step": 0.01, "unit": "SGPA", "description": "Previous semester SGPA (e.g., 8.96)", "column": "Previous_Semester_SGPA"},
            {"id": "q7", "category": "Branch", "question": "What is your branch/field of study?", "type": "multiple_choice", "options": ["Computer Science", "Information Technology", "Electronics & Telecommunication", "Mechanical", "Civil", "Electrical", "Chemical", "Biotechnology", "Other"], "column": "Branch"},
            {"id": "q8", "category": "Commute Mode", "question": "What is your primary mode of commute?", "type": "multiple_choice", "options": ["Walk", "Bicycle", "Bus", "Train/Local", "Metro", "Car/Two-wheeler", "Auto/Shared", "Other"], "column": "Commute_Mode"},
            {"id": "q9", "category": "Part Time Job", "question": "Do you have a part-time job?", "type": "multiple_choice", "options": ["No", "Yes"], "column": "Part_Time_Job"},
            {"id": "q10", "category": "Extracurricular", "question": "Do you do extracurricular activities?", "type": "multiple_choice", "options": ["No", "Yes"], "column": "Extracurricular_Activities"},
            {"id": "q11", "category": "Peer Learning", "question": "Do you engage in peer learning?", "type": "multiple_choice", "options": ["No", "Yes"], "column": "Peer_Learning"},
            {"id": "q12", "category": "Mentorship", "question": "Is mentorship available to you?", "type": "multiple_choice", "options": ["No", "Yes"], "column": "Mentorship_Available"},
            {"id": "q13", "category": "Financial Status", "question": "What is your financial status?", "type": "multiple_choice", "options": ["Low Income", "Middle Class", "Upper Middle Class", "High Income"], "column": "Financial_Status"},
            {"id": "q14", "category": "Mood", "question": "How would you rate your mood?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Very low, 10 = Very high", "column": "Mood_Score"},
            {"id": "q15", "category": "Anxiety", "question": "How anxious do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not anxious, 10 = Extremely anxious", "column": "Anxiety_Score"},
        ],
    },
    "general": {
        "dataset": "early_wakeup_health_dataset.csv",
        "model": "structured_model_health.pkl",
        "preprocessor": "preprocessor_wakeup.pkl",
        "target": "Wellness_Category",
    "questions": [
            {"id": "q1", "category": "Sleep", "question": "How many hours do you sleep per night?", "type": "number", "minValue": 0, "maxValue": 14, "step": 0.5, "unit": "hours", "description": "Hours per night (e.g., 7.5)", "column": "Sleep_Duration_Hours"},
            {"id": "q2", "category": "Sleep Quality", "question": "How is your sleep quality?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Very poor, 10 = Excellent", "column": "Sleep_Quality_Score"},
            {"id": "q3", "category": "Stress", "question": "How stressed do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not stressed, 10 = Extremely stressed", "column": "Stress_Level"},
            {"id": "q4", "category": "Fatigue", "question": "How fatigued do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not fatigued, 10 = Extremely fatigued", "column": "Fatigue_Level_Score"},
            {"id": "q5", "category": "Anxiety", "question": "How anxious do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not anxious, 10 = Extremely anxious", "column": "Anxiety_Score"},
            {"id": "q6", "category": "Mood", "question": "How would you rate your mood?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Very low, 10 = Very high", "column": "Mood_Score"},
            {"id": "q7", "category": "Energy", "question": "How energetic do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = No energy, 10 = Full energy", "column": "Energy_Level_Score"},
            {"id": "q8", "category": "Focus", "question": "How well can you focus?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Cannot focus, 10 = Fully focused", "column": "Focus_Concentration_Score"},
            {"id": "q9", "category": "Social", "question": "How socially connected do you feel?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Isolated, 10 = Very connected", "column": "Social_Interaction_Score"},
            {"id": "q10", "category": "Life", "question": "How satisfied are you with life?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not satisfied, 10 = Very satisfied", "column": "Life_Satisfaction_Score"},
            {"id": "q11", "category": "Exercise", "question": "How often do you exercise per week?", "type": "number", "minValue": 0, "maxValue": 7, "step": 1, "unit": "days", "description": "Days per week", "column": "Exercise_Frequency_Per_Week"},
            {"id": "q12", "category": "Screen Time", "question": "How many hours of screen time before bed?", "type": "number", "minValue": 0, "maxValue": 8, "step": 0.5, "unit": "hours", "description": "Hours before sleep", "column": "Screen_Time_Before_Bed_Hours"},
            {"id": "q13", "category": "Outdoor", "question": "How much outdoor time do you get daily?", "type": "number", "minValue": 0, "maxValue": 8, "step": 0.5, "unit": "hours", "description": "Hours per day", "column": "Outdoor_Time_Hours"},
            {"id": "q14", "category": "BMI", "question": "What is your BMI?", "type": "number", "minValue": 10, "maxValue": 50, "step": 0.1, "unit": "BMI", "description": "Body Mass Index (e.g., 23.4)", "column": "BMI"},
            {"id": "q15", "category": "Depression Risk", "question": "How at risk are you for depression?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = No risk, 10 = Very high risk", "column": "Depression_Risk_Score"},
            {"id": "q16", "category": "Productivity", "question": "How productive are you daily?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Not productive, 10 = Very productive", "column": "Productivity_Score"},
            {"id": "q17", "category": "Steps", "question": "How many steps do you walk daily?", "type": "number", "minValue": 0, "maxValue": 30000, "step": 100, "unit": "steps", "description": "Average daily steps", "column": "Daily_Steps"},
            {"id": "q18", "category": "Water", "question": "How many liters of water do you drink daily?", "type": "number", "minValue": 0, "maxValue": 10, "step": 0.5, "unit": "liters", "description": "Daily water intake (e.g., 2.5)", "column": "Water_Intake_Liters"},
            {"id": "q19", "category": "Immune", "question": "How strong is your immune health?", "type": "rating", "minValue": 0, "maxValue": 10, "description": "0 = Weak, 10 = Very strong", "column": "Immune_Health_Score"},
        ],
    },
    "sentiment": {
        "dataset": "Combined Data.csv",
        "model": "structured_model_combined_data.pkl",
        "preprocessor": None,
        "target": "status",
        "questions": [],
    },
}

CATEGORY_MAP = {
    "Sleep": "Sleep Duration",
    "Sleep Quality": "Sleep Quality",
    "Stress": "Stress Level",
    "Fatigue": "Fatigue Level",
    "Anxiety": "Anxiety Level",
    "Mood": "Mood",
    "Energy": "Energy Level",
    "Focus": "Focus/Concentration",
    "Social": "Social Connection",
    "Life": "Life Satisfaction",
    "Study": "Study Hours",
    "Social Media": "Social Media Usage",
    "Attendance": "Attendance",
    "Exercise": "Exercise Frequency",
    "Screen Time": "Screen Time",
    "Outdoor": "Outdoor Time",
}


def get_occupation_type(occupation: str) -> str:
    occupation_lower = occupation.lower()
    if any(word in occupation_lower for word in ["student", "university", "college", "school"]):
        return "student"
    if any(word in occupation_lower for word in ["professional", "working", "employed", "job", "engineer", "developer", "teacher", "doctor", "nurse"]):
        return "general"
    return "general"


def load_questions(occupation: str) -> list:
    occ_type = get_occupation_type(occupation)
    config = DATASET_QUESTIONS.get(occ_type, DATASET_QUESTIONS["general"])
    return config["questions"]


def load_model_features(occupation: str) -> dict:
    occ_type = get_occupation_type(occupation)
    config = DATASET_QUESTIONS.get(occ_type, DATASET_QUESTIONS["general"])

    model_path = os.path.join(MODELS_DIR, config["model"])
    features = {}

    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            if hasattr(model, 'steps'):
                for name, step in model.steps:
                    if name == 'preprocessor' and hasattr(step, 'feature_names_in_'):
                        features['model_columns'] = list(step.feature_names_in_)
                    if name == 'classifier' and hasattr(step, 'feature_importances_'):
                        importances = step.feature_importances_
                        features['feature_importances'] = importances.tolist()
        except Exception:
            pass

    return features


def generate_questions_from_columns(occupation: str) -> list:
    occ_type = get_occupation_type(occupation)
    config = DATASET_QUESTIONS.get(occ_type, DATASET_QUESTIONS["general"])

    if config["questions"]:
        return config["questions"]

    df_path = os.path.join(DATA_DIR, config["dataset"])
    if not os.path.exists(df_path):
        return config["questions"]

    df = pd.read_csv(df_path)
    questions = []

    mental_health_cols = [
        'Sleep_Hours_per_Night', 'Sleep_Duration_Hours', 'Sleep_Quality_Score',
        'Stress_Level', 'Fatigue_Level_Score', 'Mood_Score', 'Anxiety_Score',
        'Energy_Level_Score', 'Focus_Concentration_Score', 'Social_Interaction_Score',
        'Life_Satisfaction_Score', 'Study_Hours_per_Day', 'Attendance_Percentage',
        'Number_of_Night_Awakenings', 'Exercise_Frequency_Per_Week',
        'Screen_Time_Before_Bed_Hours', 'Outdoor_Time_Hours',
    ]

    rating_cols = [c for c in mental_health_cols if c in df.columns and df[c].dtype in ['float64', 'int64']]
    number_cols = [c for c in df.columns if c not in rating_cols and df[c].dtype in ['float64', 'int64'] and c not in ['Person_ID', 'Student_ID', 'Unnamed: 0']]

    for i, col in enumerate(rating_cols[:10]):
        q = {
            "id": f"q{i+1}",
            "category": col.split("_")[0].title(),
            "question": f"What is your {col.replace('_', ' ').lower()}?",
            "type": "rating",
            "minValue": 0,
            "maxValue": 10,
            "description": "Rate from 0 (low) to 10 (high)",
            "column": col,
        }
        questions.append(q)

    for i, col in enumerate(number_cols[:5]):
        if len(questions) + i >= 15:
            break
        min_val = max(0, int(df[col].min()))
        max_val = min(100, int(df[col].max())) if df[col].max() < 1000 else 100
        q = {
            "id": f"q{len(questions)+1}",
            "category": col.split("_")[0].title(),
            "question": f"What is your {col.replace('_', ' ').lower()}?",
            "type": "number",
            "minValue": min_val,
            "maxValue": max_val,
            "unit": "",
            "column": col,
        }
        questions.append(q)

    return questions[:15]
