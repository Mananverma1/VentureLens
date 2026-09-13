"""Risk Agent — identifies key risks using real search for regulatory facts."""
import litellm

from backend import config
from backend.tools.search_helper import search


def run_risk_analysis(startup_idea: str, market: str, competitor: str, business: str) -> str:
    reg_text = search(f"regulations compliance legal requirements {startup_idea[:100]}", max_results=2)

    context = f"Market: {market[:300]}\nCompetitor: {competitor[:300]}\nBusiness: {business[:300]}"

    prompt = f"""You are a risk analyst. Write a concise risk assessment (under 200 words) with likelihood/impact (Low/Med/High) and one mitigation for each:

1. Regulatory/legal risk (use the search results below)
2. Market risk
3. Competitive risk
4. Execution risk
5. Financial risk

Startup idea: {startup_idea}

Regulatory search results:
{reg_text}

Context:
{context}

Write the risk assessment now:"""

    response = litellm.completion(
        model=config.MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
        api_key=config.GROQ_API_KEY,
    )
    return response.choices[0].message.content.strip()
