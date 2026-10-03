import json
import os
import sys
from flask import Blueprint, request, jsonify

from app.utils.predict_sentiment import predict_sentiment
from app.question_generator import load_questions, get_occupation_type, load_model_features, generate_questions_from_columns

api = Blueprint("api", __name__, url_prefix="/api")


def debug_print(*args, **kwargs):
    print(*args, **kwargs, flush=True, file=sys.stderr)


CATEGORY_MAP = {
    "Sleep": "sleep",
    "Sleep Quality": "sleep",
    "Stress": "stress",
    "Fatigue": "energy",
    "Anxiety": "anxiety",
    "Mood": "mood",
    "Energy": "energy",
    "Focus": "focus",
    "Focus/Concentration": "focus",
    "Social": "social",
    "Social Media": "social",
    "Social Connection": "social",
    "Life": "self_worth",
    "Life Satisfaction": "self_worth",
    "Study": "focus",
    "Attendance": "focus",
    "Exercise": "energy",
    "Screen Time": "sleep",
    "Outdoor": "social",
    "BMI": "self_worth",
    "Depression Risk": "anxiety",
    "Productivity": "focus",
    "Steps": "energy",
    "Water": "energy",
    "Immune": "energy",
    "KT": "focus",
    "Commute": "social",
    "SGPA": "self_worth",
    "Extracurricular": "social",
    "Peer Learning": "focus",
    "Mentorship": "social",
    "Part Time Job": "energy",
    "Financial Status": "self_worth",
    "Branch": "focus",
    "Commute Mode": "social",
}


def build_category_scores(responses, questions):
    scores = {}
    counts = {}
    for q in questions:
        qid = q["id"]
        value = responses.get(qid, None)
        if value is None:
            continue
        cat = CATEGORY_MAP.get(q.get("category", ""), None)
        if cat is None:
            continue
        
        # Handle multiple choice: convert string option to numeric index (1-based)
        if q.get("type") == "multiple_choice" and q.get("options"):
            try:
                options = q["options"]
                if isinstance(value, str) and value in options:
                    value = options.index(value) + 1  # 1-based index
                else:
                    value = float(value)
            except (ValueError, TypeError):
                continue
        else:
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue
        
        min_val = q.get("minValue", 0) or 0
        max_val = q.get("maxValue", len(q.get("options", [])) if q.get("type") == "multiple_choice" else 10) or 10
        if max_val > min_val:
            normalized = ((value - min_val) / (max_val - min_val)) * 10
            normalized = max(0, min(10, normalized))
        else:
            normalized = value
        
        if cat in scores:
            scores[cat] += normalized
            counts[cat] += 1
        else:
            scores[cat] = normalized
            counts[cat] = 1

    # Average scores for each category
    for cat in scores:
        if counts[cat] > 0:
            scores[cat] = scores[cat] / counts[cat]

    defaults = {"stress": 5, "sleep": 6, "self_worth": 5, "anxiety": 5, "mood": 5, "focus": 5, "social": 5, "energy": 5}
    for cat, default in defaults.items():
        if cat not in scores:
            scores[cat] = default

    return scores


def _stress_level(value):
    if value <= 3:
        return "Low"
    elif value <= 6:
        return "Medium"
    return "High"


def predict_student_structured(responses):
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "structured_model_student.pkl")
    if not os.path.exists(model_path):
        return 0.5
    try:
        import pandas as pd
        import joblib
        model = joblib.load(model_path)
        features = {
            "Age": float(responses.get("age", 21)),
            "Stress_Level": _stress_level(float(responses.get("q1", 5))),
            "Study_Hours_per_Day": float(responses.get("q2", 4)),
            "Attendance_Percentage": float(responses.get("q3", 75)),
            "Sleep_Hours_per_Night": float(responses.get("q4", 7)),
            "Social_Media_Hours_per_Day": float(responses.get("q5", 3)),
            "Previous_Semester_SGPA": float(responses.get("q6", 6.0)),
            "Branch": responses.get("q7", "Information Technology"),
            "Commute_Mode": responses.get("q8", "Local Train"),
            "Part_Time_Job": responses.get("q9", "No"),
            "Extracurricular_Activities": responses.get("q10", "Yes"),
            "Peer_Learning": responses.get("q11", "Yes"),
            "Mentorship_Available": responses.get("q12", "No"),
            "Financial_Status": responses.get("q13", "Middle Class"),
            "Gender": responses.get("gender", "Male"),
            "Year_of_Study": responses.get("year", "Second Year"),
            "Cleared_in_First_Attempt": responses.get("cleared_first_attempt", "Yes"),
            "Commute_Time_mins": 30,  # Default commute time
            "Number_of_KTs": 0,       # Default no backlogs
        }
        df = pd.DataFrame([features])
        prob = model.predict_proba(df)[0][1]
        return float(prob)
    except Exception as e:
        import sys
        print(f"Student model prediction error: {e}", file=sys.stderr)
        return 0.5


@api.route("/mental-health/questions", methods=["GET"])
def get_questions():
    occupation = request.args.get("occupation", "")
    questions = load_questions(occupation)
    if not questions:
        questions = generate_questions_from_columns(occupation)
    return jsonify(questions)


@api.route("/mental-health/model-columns", methods=["GET"])
def model_columns():
    occupation = request.args.get("occupation", "")
    features = load_model_features(occupation)
    return jsonify(features)


@api.route("/mental-health/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    name = data.get("name", "")
    date_of_birth = data.get("dateOfBirth", "")
    age = data.get("age", 0)
    occupation = data.get("occupation", "")
    responses = data.get("responses", {})

    occ_type = get_occupation_type(occupation)
    questions = load_questions(occupation)
    if not questions:
        questions = generate_questions_from_columns(occupation)

    category_scores = build_category_scores(responses, questions)

    structured_prob = 0.5
    if occ_type == "student":
        structured_prob = predict_student_structured(responses)

    nlp_score = 0.5

    from fuzzy_logic.fuzzy_engine import run_fuzzy_engine
    wellness_data = run_fuzzy_engine(category_scores, structured_prob, nlp_score)
    wellness_score = wellness_data["wellness_score"]

    if wellness_score >= 75:
        category = "Excellent"
    elif wellness_score >= 55:
        category = "Good"
    elif wellness_score >= 35:
        category = "Moderate"
    else:
        category = "Needs Attention"

    def get_val(qid):
        for q in questions:
            if q["id"] == qid:
                val = responses.get(qid, 0)
                if q.get("type") == "number":
                    if q.get("category") == "Sleep":
                        return val
                    elif q.get("category") == "Study":
                        return val
                    elif q.get("category") == "Social Media":
                        return val
                    elif q.get("category") == "Attendance":
                        return val
                    elif q.get("category") == "Exercise":
                        return val
                    elif q.get("category") == "Screen Time":
                        return val
                    elif q.get("category") == "Outdoor":
                        return val
                    elif q.get("category") == "SGPA":
                        return val
                    elif q.get("category") == "KT":
                        return val
                    elif q.get("category") == "Commute":
                        return val
                return val
        return 0

    areas_to_improve = []

    for q in questions:
        qid = q["id"]
        value = responses.get(qid, None)
        if value is None:
            continue

        label = q["category"]
        if q.get("type") == "number":
            if q.get("category") == "Sleep":
                threshold = value < 6
                current = f"{value} hours/night"
            elif q.get("category") == "Study":
                threshold = value < 2
                current = f"{value} hours/day"
            elif q.get("category") == "Social Media":
                threshold = value > 4
                current = f"{value} hours/day"
            elif q.get("category") == "Attendance":
                threshold = value < 70
                current = f"{value}%"
            elif q.get("category") == "Exercise":
                threshold = value < 3
                current = f"{value} days/week"
            elif q.get("category") == "Screen Time":
                threshold = value > 2
                current = f"{value} hours before bed"
            elif q.get("category") == "Outdoor":
                threshold = value < 1
                current = f"{value} hours/day"
            elif q.get("category") == "BMI":
                threshold = value > 30
                current = f"{value} BMI"
            elif q.get("category") == "Steps":
                threshold = value < 5000
                current = f"{value} steps"
            elif q.get("category") == "Water":
                threshold = value < 2
                current = f"{value} liters"
            elif q.get("category") == "SGPA":
                threshold = value < 5.0
                current = f"{value} SGPA"
            elif q.get("category") == "KT":
                threshold = value > 0
                current = f"{value} backlogs"
            elif q.get("category") == "Commute":
                threshold = value > 60
                current = f"{value} mins"
            else:
                threshold = False
                current = f"{value}"
        else:
            try:
                value = float(value)
            except (TypeError, ValueError):
                threshold = False
                current = f"{value}"
            else:
                if label in ["Mood", "Energy", "Energy Level", "Social", "Social Connection", "Social Support",
                             "Life", "Life Satisfaction", "Sleep Quality", "Focus", "Study", "Attendance",
                             "Exercise", "Outdoor", "Productivity", "Immune"]:
                    threshold = value < 5
                else:
                    threshold = value > 5
                current = f"{value}/10"

        if threshold:
            rec_map = {
                "Sleep": ("Aim for 7-9 hours. Maintain consistent sleep/wake times.", "Set a consistent bedtime and wake-up time."),
                "Stress": ("Practice stress management: deep breathing, journaling, time management.", "Try a 10-minute relaxation technique daily."),
                "Sleep Quality": ("Improve sleep hygiene: limit screens, create dark/cool environment.", "Avoid screens 30 min before bed."),
                "Fatigue": ("Ensure adequate rest, nutrition, and hydration.", "Take short breaks during demanding tasks."),
                "Anxiety": ("Practice mindfulness, progressive muscle relaxation, or cognitive reframing.", "Try 5 minutes of mindful breathing."),
                "Mood": ("Regular physical activity, social engagement, and sunlight exposure.", "Engage in 30 minutes of physical activity."),
                "Energy": ("Ensure balanced nutrition, hydration, and regular movement.", "Stay hydrated and eat balanced meals."),
                "Focus": ("Break tasks into smaller steps. Use Pomodoro or similar techniques.", "Try the Pomodoro technique (25 min work, 5 min break)."),
                "Social": ("Reach out to friends or family regularly.", "Send a message to someone you care about."),
                "Life": ("Practice gratitude, set meaningful goals, and celebrate small wins.", "Write down 3 things you are grateful for today."),
                "Study": ("Maintain consistent study schedule and take regular breaks.", "Use active recall and spaced repetition techniques."),
                "Social Media": ("Set time limits for social media. Engage in offline activities.", "Try a digital detox for one day per week."),
                "Attendance": ("Maintain regularity. Missing classes affects learning outcomes.", "Set reminders for class schedules."),
                "Exercise": ("Aim for at least 3-4 days of physical activity per week.", "Start with 20-minute walks and gradually increase."),
                "Screen Time": ("Reduce screen time before bed. Use blue light filters.", "Set a screen curfew 1 hour before sleep."),
                "Outdoor": ("Spend more time outdoors for fresh air and sunlight.", "Schedule 30 minutes outdoor time daily."),
                "BMI": ("Maintain a healthy weight through balanced diet and exercise.", "Consult a nutritionist for a personalized meal plan."),
                "Depression Risk": ("Practice mindfulness, social engagement, and seek professional help if needed.", "Talk to a counselor about your feelings."),
                "Productivity": ("Break tasks into smaller goals. Use time management techniques.", "Try the Pomodoro technique (25 min work, 5 min break)."),
                "Steps": ("Aim for at least 8,000-10,000 steps daily for good health.", "Take short walking breaks every hour."),
                "Water": ("Drink at least 8 glasses (2 liters) of water daily.", "Set hourly water intake reminders."),
                "Immune": ("Maintain a balanced diet rich in vitamins and minerals.", "Ensure adequate sleep and regular exercise."),
                "SGPA": ("Set academic goals and seek tutoring support for weak subjects.", "Meet with an academic advisor to plan improvement strategy."),
                "KT": ("Focus on consistent study habits and seek help early.", "Join study groups and address concepts you find difficult."),
                "Commute": ("Consider alternative transport or optimize your schedule.", "Use commute time for productive activities like audio learning."),
            }
            rec = rec_map.get(label, ("Maintain healthy habits.", "Continue your current routine."))
            areas_to_improve.append({
                "category": label,
                "current": current,
                "recommendation": rec[0],
                "action": rec[1],
            })

    if not areas_to_improve:
        areas_to_improve.append({
            "category": "Overall",
            "current": f"Wellness score: {wellness_score:.1f}/100",
            "recommendation": "Keep up your healthy habits!",
            "action": "Continue your current routine.",
        })

    strengths = []
    for q in questions:
        value = responses.get(q["id"], 0)
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if value >= 7:
            cat = q.get("category", "")
            if cat in ["Mood", "Mood Score"]:
                strengths.append("Positive mood")
            elif cat in ["Social", "Social Connection", "Social Support"]:
                strengths.append("Strong social connections")
            elif cat in ["Life", "Life Satisfaction"]:
                strengths.append("High life satisfaction")
            elif cat in ["Energy", "Energy Level"]:
                strengths.append("High energy levels")
            elif cat in ["Focus", "Focus/Concentration"]:
                strengths.append("Good focus and concentration")
            elif cat in ["Sleep Quality", "Sleep"]:
                strengths.append("Good sleep quality")
    if not strengths:
        strengths.append("Willingness to participate in self-assessment")

    notes = [
        f"Based on your responses, your wellness score is {wellness_score:.1f}/100.",
        f"Risk level: {wellness_data['risk_level']}.",
        "This assessment is a general indicator and not a clinical diagnosis.",
        "Please consult a mental health professional for personalized guidance.",
    ]

    return jsonify({
        "score": round(wellness_score, 1),
        "category": category,
        "strengths": strengths,
        "areas_to_improve": areas_to_improve,
        "notes": notes,
    })


@api.route("/sentiment/analyze", methods=["POST"])
def sentiment():
    data = request.get_json(force=True)
    text = data.get("text", "")
    result = predict_sentiment(text)

    return jsonify({
        "sentiment": result.get("sentiment", "Neutral"),
        "score": result.get("polarity_score", 0.0),
        "emotions": result.get("emotions", []),
        "predicted_class": result.get("label", "Normal"),
        "clinical_confidence": result.get("confidence", 0.0),
        "vader_compound": result.get("vader_compound", 0.0),
        "all_probabilities": result.get("all_probabilities", {}),
    })
