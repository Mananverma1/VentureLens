"""
VentureLens orchestrator.

Pipeline:
    Startup idea
         |
    Market -> Competitor -> Customer   (sequential, free-tier TPM safe)
         |
    Business Agent
         |
     Risk Agent
         |
   Synthesis Agent  ->  final scored verdict

Agents run sequentially to stay within Groq's free-tier 8k TPM limit.
Every agent call is wrapped with run_with_retry() so a transient
rate-limit error causes a timed wait + retry instead of a 500 crash.
"""
import time
from threading import Lock
from typing import TypedDict

from backend.agents.business_agent import run_business_analysis
from backend.agents.competitor_agent import run_competitor_analysis
from backend.agents.customer_agent import run_customer_analysis
from backend.agents.market_agent import run_market_analysis
from backend.agents.risk_agent import run_risk_analysis
from backend.agents.synthesis_agent import run_synthesis
from backend.analysis_cache import analysis_id, canonicalize_idea, get_cached, save_cached
from backend.utils import run_with_retry


_analysis_lock = Lock()


class AnalysisResult(TypedDict):
    startup_idea: str
    analysis_id: str
    market_report: str
    competitor_report: str
    customer_report: str
    business_report: str
    risk_report: str
    synthesis: dict
    elapsed_seconds: float


def analyze_startup(startup_idea: str) -> AnalysisResult:
    startup_idea = canonicalize_idea(startup_idea)
    if not startup_idea:
        raise ValueError("startup_idea must be a non-empty description of the idea.")

    with _analysis_lock:
        cached_result = get_cached(startup_idea)
        if cached_result is not None:
            return cached_result

        start = time.time()

        # Stage 1 — research agents (sequential, rate-limit safe)
        market_report    = run_with_retry(run_market_analysis,    startup_idea)
        competitor_report = run_with_retry(run_competitor_analysis, startup_idea)
        customer_report  = run_with_retry(run_customer_analysis,  startup_idea)

        # Stage 2 — business model assessment
        business_report = run_with_retry(
            run_business_analysis,
            startup_idea, market_report, competitor_report, customer_report,
        )

        # Stage 3 — risk analysis
        risk_report = run_with_retry(
            run_risk_analysis,
            startup_idea, market_report, competitor_report, business_report,
        )

        # Stage 4 — final synthesis verdict
        synthesis = run_with_retry(
            run_synthesis,
            startup_idea, market_report, competitor_report, customer_report,
            business_report, risk_report,
        )

        result = {
            "startup_idea": startup_idea,
            "analysis_id": analysis_id(startup_idea),
            "market_report": market_report,
            "competitor_report": competitor_report,
            "customer_report": customer_report,
            "business_report": business_report,
            "risk_report": risk_report,
            "synthesis": synthesis,
            "elapsed_seconds": round(time.time() - start, 1),
        }
        save_cached(startup_idea, result)
        return result
