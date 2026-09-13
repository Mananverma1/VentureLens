"""Customer Agent — researches target customers and gauges real sentiment."""
import litellm

from backend import config
from backend.tools.search_helper import search
from backend.tools.sentiment_tool import analyze_sentiment


def run_customer_analysis(startup_idea: str) -> str:
    search_text = search(f"user problems complaints reviews {startup_idea[:120]}", max_results=3)

    # Extract short snippets for sentiment analysis
    snippets = [s.strip() for s in search_text.split(". ") if len(s.strip()) > 40][:5]
    sentiment_summary = "Sentiment analysis unavailable"
    breakdown = {}
    if snippets:
        try:
            result = analyze_sentiment(snippets)
            sentiment_summary = result.get("summary", sentiment_summary)
            breakdown = result.get("breakdown_percent", {})
        except Exception:
            pass

    prompt = f"""You are a customer researcher. Based on the search results and sentiment data below, write a concise customer analysis (under 200 words) covering:
1. Target customer segment (who they are, what triggers the need)
2. Sentiment breakdown: {breakdown} — {sentiment_summary}
3. Key unmet need or current workaround

Startup idea: {startup_idea}

Search results:
{search_text[:1500]}

Write the analysis now:"""

    response = litellm.completion(
        model=config.MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
        api_key=config.GROQ_API_KEY,
    )
    return response.choices[0].message.content.strip()
