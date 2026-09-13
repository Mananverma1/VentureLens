"""
Plain-Python financial calculations for the Business Agent.

The whole point of this tool is that the LLM never invents numbers like
CAC, LTV, or break-even — it calls these deterministic functions and
narrates the result. Every formula below is a standard, textbook
definition; nothing is fabricated or approximated by a model.
"""
from strands import tool


@tool
def unit_economics(
    customer_acquisition_cost: float,
    average_revenue_per_user: float,
    gross_margin_percent: float,
    average_customer_lifespan_months: float,
) -> dict:
    """
    Compute core SaaS/startup unit economics: LTV, LTV:CAC ratio, and
    payback period.

    Args:
        customer_acquisition_cost: Fully-loaded cost (₹ or $) to acquire one customer (CAC).
        average_revenue_per_user: Average revenue per user per month (ARPU).
        gross_margin_percent: Gross margin as a percentage, e.g. 70 for 70%.
        average_customer_lifespan_months: Average months a customer stays before churning.

    Returns:
        A dict with ltv, ltv_to_cac_ratio, payback_period_months, and a
        plain-language verdict on whether the economics look healthy.
    """
    margin = gross_margin_percent / 100.0
    monthly_gross_profit = average_revenue_per_user * margin

    ltv = monthly_gross_profit * average_customer_lifespan_months
    ltv_to_cac = ltv / customer_acquisition_cost if customer_acquisition_cost else float("inf")
    payback_months = (
        customer_acquisition_cost / monthly_gross_profit if monthly_gross_profit else float("inf")
    )

    if ltv_to_cac >= 3:
        verdict = "Healthy — LTV:CAC of 3:1 or higher is the standard benchmark for a scalable model."
    elif ltv_to_cac >= 1:
        verdict = "Marginal — the business recovers acquisition cost but has thin margin for growth spend."
    else:
        verdict = "Unhealthy — CAC exceeds lifetime value; this model loses money per customer as structured."

    return {
        "status": "success",
        "content": [{
            "text": (
                f"LTV: {ltv:.2f} | LTV:CAC = {ltv_to_cac:.2f} | "
                f"CAC payback = {payback_months:.1f} months | {verdict}"
            )
        }],
        "ltv": round(ltv, 2),
        "ltv_to_cac_ratio": round(ltv_to_cac, 2),
        "payback_period_months": round(payback_months, 2),
        "verdict": verdict,
    }


@tool
def breakeven_analysis(
    fixed_costs_per_month: float,
    price_per_unit: float,
    variable_cost_per_unit: float,
) -> dict:
    """
    Compute the break-even point in units and revenue.

    Args:
        fixed_costs_per_month: Total fixed monthly costs (rent, salaries, tooling, etc.).
        price_per_unit: Selling price per unit/subscription/order.
        variable_cost_per_unit: Variable cost incurred per unit sold.

    Returns:
        A dict with breakeven_units and breakeven_revenue.
    """
    contribution_margin = price_per_unit - variable_cost_per_unit
    if contribution_margin <= 0:
        return {
            "status": "error",
            "content": [{
                "text": (
                    "Break-even is impossible at these numbers: variable cost per unit "
                    f"({variable_cost_per_unit}) meets or exceeds price ({price_per_unit}), "
                    "so contribution margin is zero or negative."
                )
            }],
        }

    breakeven_units = fixed_costs_per_month / contribution_margin
    breakeven_revenue = breakeven_units * price_per_unit

    return {
        "status": "success",
        "content": [{
            "text": (
                f"Break-even at {breakeven_units:.1f} units/month "
                f"(~{breakeven_revenue:.2f} in monthly revenue)."
            )
        }],
        "breakeven_units": round(breakeven_units, 1),
        "breakeven_revenue": round(breakeven_revenue, 2),
        "contribution_margin_per_unit": round(contribution_margin, 2),
    }


@tool
def growth_scenarios(
    starting_customers: int,
    monthly_growth_rate_percent: float,
    monthly_churn_rate_percent: float,
    months: int = 12,
) -> dict:
    """
    Project customer count month-by-month under a constant growth and
    churn rate, e.g. to compare "India vs USA" or optimistic/pessimistic
    what-if scenarios.

    Args:
        starting_customers: Customer count at month 0.
        monthly_growth_rate_percent: New-customer growth rate per month, e.g. 15 for 15%.
        monthly_churn_rate_percent: Customer churn rate per month, e.g. 5 for 5%.
        months: Number of months to project forward (default 12).

    Returns:
        A dict with the month-by-month projection and the final customer count.
    """
    growth = monthly_growth_rate_percent / 100.0
    churn = monthly_churn_rate_percent / 100.0

    projection = [round(starting_customers)]
    customers = float(starting_customers)
    for _ in range(months):
        customers = customers * (1 + growth) * (1 - churn)
        projection.append(round(customers, 1))

    return {
        "status": "success",
        "content": [{
            "text": (
                f"Projected {starting_customers} -> {projection[-1]} customers "
                f"over {months} months at {monthly_growth_rate_percent}% growth / "
                f"{monthly_churn_rate_percent}% churn."
            )
        }],
        "monthly_projection": projection,
        "final_customers": projection[-1],
    }
