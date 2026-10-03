from flask import Blueprint, render_template, request, session, redirect, url_for
from app.utils.predict_sentiment import predict_sentiment
from app.utils.predict_structured import predict_structured
from app.utils.aggregate_scores import aggregate_sentiment_results

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["age"] = request.form.get("age")
        session["gender"] = request.form.get("gender")
        return redirect(url_for("main.section_b"))
    return render_template("section_a_basic_info.html")


@main.route("/section-b", methods=["GET", "POST"])
def section_b():
    if request.method == "POST":
        session["section_b"] = {
            "q1": int(request.form.get("q1", 5)),
            "q2": int(request.form.get("q2", 5)),
            "q3": int(request.form.get("q3", 5)),
            "q4": int(request.form.get("q4", 5)),
            "q5": int(request.form.get("q5", 5)),
            "q6": int(request.form.get("q6", 5)),
            "q7": int(request.form.get("q7", 5)),
            "q8": int(request.form.get("q8", 5)),
            "q9": int(request.form.get("q9", 5)),
            "q10": int(request.form.get("q10", 5)),
        }
        return redirect(url_for("main.section_c"))
    return render_template("section_b_scale_questions.html")


@main.route("/section-c", methods=["GET", "POST"])
def section_c():
    if request.method == "POST":
        texts = [
            request.form.get("text1", ""),
            request.form.get("text2", ""),
            request.form.get("text3", ""),
            request.form.get("text4", ""),
            request.form.get("text5", ""),
        ]
        results = [predict_sentiment(t) for t in texts if t.strip()]
        aggregated = aggregate_sentiment_results(results)
        session["nlp_score"] = aggregated["nlp_score"]
        return redirect(url_for("main.result"))
    return render_template("section_c_text_questions.html")


@main.route("/result", methods=["GET"])
def result():
    from fuzzy_logic.fuzzy_engine import run_fuzzy_engine

    section_b = session.get("section_b", {})
    nlp_score = session.get("nlp_score", 0.5)

    category_scores = {
        "stress": section_b.get("q1", 5),
        "sleep": 11 - section_b.get("q2", 5),
        "self_worth": section_b.get("q9", 5),
        "anxiety": section_b.get("q8", 5),
        "mood": 11 - section_b.get("q6", 5),
        "focus": section_b.get("q4", 5),
        "social": section_b.get("q5", 5),
        "energy": 11 - section_b.get("q10", 5),
    }

    structured_prob = predict_structured(session.get("section_b", {}))

    result_data = run_fuzzy_engine(category_scores, structured_prob, nlp_score)
    return render_template("result.html", result=result_data)
