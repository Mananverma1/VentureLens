"""
Customer-sentiment tool for the Customer Agent.

Uses cardiffnlp/twitter-roberta-base-sentiment-latest — a real, dedicated,
pre-trained text-classification model — run locally via the Transformers
pipeline. This is the model named in the project plan; nothing here is a
keyword heuristic standing in for it.

The model is loaded once (lazily, on first use) and cached for the life
of the process so repeated calls don't reload weights every time.
"""
from functools import lru_cache

from strands import tool

from backend import config

_LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
    # some pipeline versions already return human labels directly
    "negative": "negative",
    "neutral": "neutral",
    "positive": "positive",
}


@lru_cache(maxsize=1)
def _get_pipeline():
    from transformers import pipeline

    return pipeline(
        "sentiment-analysis",
        model=config.SENTIMENT_MODEL_ID,
        tokenizer=config.SENTIMENT_MODEL_ID,
    )


@tool
def analyze_sentiment(texts: list[str]) -> dict:
    """
    Run real sentiment analysis over a batch of customer-facing text
    (reviews, tweets, forum comments, survey responses) using
    cardiffnlp/twitter-roberta-base-sentiment-latest.

    Args:
        texts: A list of raw text snippets to classify. Keep each under
            ~500 characters (the model truncates longer inputs).

    Returns:
        A dict with per-text sentiment labels/scores plus an aggregate
        positive/neutral/negative breakdown.
    """
    if not texts:
        return {
            "status": "error",
            "content": [{"text": "No texts provided to analyze_sentiment."}],
        }

    clf = _get_pipeline()
    raw_results = clf(texts, truncation=True)

    per_text = []
    counts = {"positive": 0, "neutral": 0, "negative": 0}
    for text, result in zip(texts, raw_results):
        label = _LABEL_MAP.get(result["label"], result["label"].lower())
        counts[label] = counts.get(label, 0) + 1
        per_text.append({
            "text": text,
            "sentiment": label,
            "confidence": round(float(result["score"]), 4),
        })

    total = len(texts)
    breakdown = {k: round(100 * v / total, 1) for k, v in counts.items()}

    summary = (
        f"{total} texts analyzed: {breakdown.get('positive', 0)}% positive, "
        f"{breakdown.get('neutral', 0)}% neutral, {breakdown.get('negative', 0)}% negative."
    )

    return {
        "status": "success",
        "content": [{"text": summary}],
        "per_text": per_text,
        "breakdown_percent": breakdown,
        "summary": summary,
    }
