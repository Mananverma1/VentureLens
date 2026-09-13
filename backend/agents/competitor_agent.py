"""Competitor Agent — finds real competitors via search."""
import litellm

from backend import config
from backend.tools.search_helper import search


def run_competitor_analysis(startup_idea: str) -> str:
    search_text = search(f"competitors alternatives companies {startup_idea[:120]}", max_results=3)

    prompt = f"""You are a competitive analyst. Based ONLY on the search results below, write a concise competitor analysis (under 200 words) covering:
1. 3-5 real competing companies (name, what they do, one weakness)
2. How crowded/defensible is this space?

Never invent company names — only use what appears in the search results.

Startup idea: {startup_idea}

Search results:
{search_text}

Write the analysis now:"""

    response = litellm.completion(
        model=config.MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
        api_key=config.GROQ_API_KEY,
    )
    return response.choices[0].message.content.strip()
