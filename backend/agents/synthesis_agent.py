"""
Synthesis Agent — combines all findings into one final scored verdict.
Uses direct LiteLLM calls to stay within free-tier TPM limits.
"""
import json
import re

import litellm

from backend import config


def _extract_json(raw_text: str) -> dict:
    """Extract JSON from model output regardless of wrapping."""
    text = raw_text.strip()

    # 1. <result> tags
    m = re.search(r"<result>\s*(\{.*?\})\s*</result>", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        # 2. markdown fences
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            text = m.group(1)
        else:
            # 3. last JSON block containing startup_score
            for candidate in reversed(list(re.finditer(r"\{[^{}]*\}", text, re.DOTALL))):
                if "startup_score" in candidate.group(0):
                    text = candidate.group(0)
                    break
            else:
                m = re.search(r"\{.*\}", text, re.DOTALL)
                if m:
                    text = m.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "startup_score": None,
            "recommendation": None,
            "top_strengths": [],
            "top_risks": [],
            "key_assumptions_to_validate": [],
            "summary": raw_text.strip(),
            "parse_warning": "Model response could not be parsed as JSON; raw output is in 'summary'.",
        }


def run_synthesis(
    startup_idea: str,
    market: str, competitor: str, customer: str,
    business: str, risk: str,
) -> dict:
    # Trim each report to keep total prompt under 4k tokens
    def trim(s, n=350):
        return s[:n] + "..." if len(s) > n else s

    prompt = f"""You are the final analyst in a startup evaluation pipeline.

Startup idea: {startup_idea}

Market report: {trim(market)}
Competitor report: {trim(competitor)}
Customer report: {trim(customer)}
Business report: {trim(business)}
Risk report: {trim(risk)}

Based on the above, output ONLY a JSON object inside <result> tags:

<result>
{{
  "startup_score": <integer 0-100>,
  "recommendation": "<Strong Go | Go with caveats | Needs major rework | No-go>",
  "top_strengths": ["...", "...", "..."],
  "top_risks": ["...", "...", "..."],
  "key_assumptions_to_validate": ["...", "..."],
  "summary": "<3-5 sentence plain-language verdict>"
}}
</result>

Score honestly: mediocre ideas score 30-50, weak ideas below 30."""

    response = litellm.completion(
        model=config.MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=900,
        temperature=0.2,
        api_key=config.GROQ_API_KEY,
    )
    raw = response.choices[0].message.content.strip()
    return _extract_json(raw)
