"""
Sentiment inference for the mental-health statement classifier.

Two independent signals are combined:

1. Clinical classification - models/structured_model_sentiment.pkl is a Pipeline
   (word + char TF-IDF FeatureUnion -> LogisticRegression) trained on Combined Data.csv
   across 7 classes: Anxiety, Bipolar, Depression, Normal, Personality disorder,
   Stress, Suicidal. It answers "which condition does this text describe?".

2. Polarity - VADER answers "is this text positive or negative?". This is kept separate
   on purpose: the training data has no positive class. "Normal" is a catch-all for
   neutral Reddit chatter, not a happy class, so the clinical model alone labels cheerful
   text such as "i am very happy" as Depression (people write "I'm not happy" in those
   threads). Polarity therefore has to come from a sentiment-aware model.

The two signals feed different fields, because the UI renders them differently:

- "Sentiment Result" + "Confidence"  -> polarity (VADER). score is |compound|, the
  strength of the positive/negative direction, so it is consistent with the verdict.
- "Emotions detected"                -> emotional tone words found in the text.
  Deliberately NOT the clinical class labels: the dataset has no positive class, so
  "i am very happy" comes back from the clinical model as Depression 59%, and telling
  a user that under a heading about emotions would be both alarming and wrong.
- predicted_class / all_probabilities -> the clinical 7-class model, returned for the
  assessment flow and for debugging. The sentiment screen does not display these.
"""

import os
import re

import joblib

from app.utils.text_cleaning import clean_text

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")

NEGATIVE_EMOTION_WORDS = (
    "sad", "depressed", "anxious", "worried", "stressed", "tired", "hopeless",
    "angry", "fear", "pain", "alone", "lonely", "upset", "overwhelmed", "miserable",
)
POSITIVE_EMOTION_WORDS = (
    "happy", "good", "great", "wonderful", "excited", "calm", "peaceful", "grateful",
    "love", "joy", "hope", "better", "fine", "okay", "well", "motivated", "confident",
    "proud", "content", "relaxed", "glad", "cheerful",
)

_sentiment_model = None
_sentiment_le = None
_vader = None


def _load_model():
    global _sentiment_model, _sentiment_le
    if _sentiment_model is None:
        _sentiment_model = joblib.load(
            os.path.join(MODELS_DIR, "structured_model_sentiment.pkl")
        )
        _sentiment_le = joblib.load(
            os.path.join(MODELS_DIR, "label_encoder_sentiment.pkl")
        )
    return _sentiment_model, _sentiment_le


def _get_vader():
    global _vader
    if _vader is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

            _vader = SentimentIntensityAnalyzer()
        except ImportError:
            _vader = False
    return _vader or None


def _detect_emotion_words(text: str) -> list:
    """Emotional tone words literally present in the text, for the emotions chips.

    Matched on word boundaries: plain substring matching reported "Hope" inside
    "hopeless", which is the opposite of the intended reading.
    """
    text_lower = text.lower()
    emotions = []
    for word in NEGATIVE_EMOTION_WORDS + POSITIVE_EMOTION_WORDS:
        matches = len(re.findall(rf"\b{re.escape(word)}\b", text_lower))
        if matches:
            emotions.append(
                {
                    "label": word.capitalize(),
                    "score": min(0.5 + matches * 0.1, 0.99),
                }
            )
    return emotions


def predict_sentiment(text: str) -> dict:
    model, label_encoder = _load_model()

    cleaned = clean_text(text)
    if not cleaned:
        return {
            "label": "Normal",
            "confidence": 0.0,
            "sentiment": "Neutral",
            "polarity_score": 0.0,
            "vader_compound": 0.0,
            "all_probabilities": {},
            "emotions": [],
        }

    # The pipeline owns the vectorizer, so hand it cleaned raw text.
    proba = model.predict_proba([cleaned])[0]
    predicted_index = int(proba.argmax())
    label = label_encoder.inverse_transform([predicted_index])[0]
    clinical_confidence = float(proba.max())

    all_probabilities = {
        cls: float(p) for cls, p in zip(label_encoder.classes_, proba)
    }

    vader = _get_vader()
    if vader is not None:
        scores = vader.polarity_scores(cleaned)
        compound = float(scores["compound"])
    else:
        compound = 0.0

    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "label": label,
        "confidence": clinical_confidence,
        "sentiment": sentiment,
        # Strength of the polarity verdict, consistent with the sentiment word shown.
        "polarity_score": abs(compound),
        "vader_compound": compound,
        "all_probabilities": all_probabilities,
        "emotions": _detect_emotion_words(cleaned),
    }
