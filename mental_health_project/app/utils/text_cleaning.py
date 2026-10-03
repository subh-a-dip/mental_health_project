"""
Text normalisation shared by training and inference.

The sentiment model is a Pipeline whose first step is a fitted word+char TF-IDF
FeatureUnion. That vectorizer was fitted on text that had already been passed
through clean_text(), so the exact same function must run before predict() at
serve time. Keeping one copy here is what stops training and serving from drifting.
"""

import re

_URL_RE = re.compile(r"http\S+|www\.\S+")
_NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text):
    """Lowercase, strip URLs and punctuation, collapse whitespace."""
    if text is None:
        return ""
    text = str(text)
    text = _URL_RE.sub(" ", text)
    text = _NON_ALPHA_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip().lower()
    return text
