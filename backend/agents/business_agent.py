"""
Business Agent — assesses business model using deterministic finance tools.
Uses direct LiteLLM calls to stay within free-tier TPM limits.
"""
import litellm

from backend import config
from backend.tools.finance_calculator import (
    breakeven_analysis,
    growth_scenarios,
    unit_economics,
)


def run_business_analysis(startup_idea: str, market: str, competitor: str, customer: str) -> str:
    # Run finance tools with reasonable assumptions for a SaaS/digital startup
    ue = unit_economics(
        customer_acquisition_cost=150.0,
        average_revenue_per_user=30.0,
        gross_margin_percent=70.0,
        average_customer_lifespan_months=18.0,
    )
    be = breakeven_analysis(
        fixed_costs_per_month=5000.0,
        price_per_unit=30.0,
        variable_cost_per_unit=9.0,
    )
    gs = growth_scenarios(
        starting_customers=100,
        monthly_growth_rate_percent=15.0,
        monthly_churn_rate_percent=5.0,
        months=12,
    )

    finance_summary = (
        f"Unit economics: {ue['content'][0]['text']}\n"
        f"Break-even: {be['content'][0]['text']}\n"
        f"Growth (100 customers, 15% growth, 5% churn, 12mo): {gs['content'][0]['text']}"
    )

    # Trim context to avoid TPM overflow
    context = f"Market: {market[:400]}\nCompetitor: {competitor[:400]}\nCustomer: {customer[:400]}"

    prompt = f"""You are a business analyst. Using the finance tool results below (treat assumptions as estimates), write a concise business model assessment (under 200 words) covering:
1. Likely revenue model
2. What the finance numbers say (use the computed figures, do not recalculate)
3. The biggest fragility in the cost structure

Startup idea: {startup_idea}

Finance tool results (computed, not estimated):
{finance_summary}

Context from other agents:
{context}

Write the assessment now:"""

    response = litellm.completion(
        model=config.MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3,
        api_key=config.GROQ_API_KEY,
    )
    return response.choices[0].message.content.strip()
