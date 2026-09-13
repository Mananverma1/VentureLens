"""Market Agent — sizes the market and surfaces current trends via real web search."""
import litellm

from backend import config
from backend.tools.search_helper import search


def run_market_analysis(startup_idea: str) -> str:
    search_text = search(f"market size growth trends {startup_idea[:120]}", max_results=3)

    prompt = f"""You are a market analyst. Based ONLY on the search results below, write a concise market assessment (under 200 words) covering:
1. Target customer (1-2 sentences)
2. Market size / TAM with source
3. Growth trend
4. Is now a good time to enter?

Startup idea: {startup_idea}

Search results:
{search_text}

Write the assessment now:"""

    response = litellm.completion(
        model=config.MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
        api_key=config.GROQ_API_KEY,
    )
    return response.choices[0].message.content.strip()
