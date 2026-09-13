"""
VentureLens backend API.

Run with:
    cd backend
    uvicorn main:app --reload --port 8000

Then:
    curl -X POST http://localhost:8000/analyze \\
         -H "Content-Type: application/json" \\
         -d '{"startup_idea": "A subscription meal-kit service for..."}'
"""
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.analysis_cache import get_latest
from backend.orchestrator import analyze_startup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("venturelens")

app = FastAPI(
    title="VentureLens API",
    description="Multi-agent startup idea analyzer (Strands Agents + Hugging Face models).",
    version="0.1.0",
)

# Wide-open CORS for local hackathon development. Tighten this before any
# real deployment (restrict allow_origins to your actual frontend origin).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    startup_idea: str = Field(
        ..., min_length=10,
        description="Free-text description of the startup idea to analyze.",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/analysis/latest")
def latest_analysis():
    """Return the latest analysis created through the frontend or API."""
    result = get_latest()
    if result is None:
        raise HTTPException(status_code=404, detail="No completed analysis is available yet.")
    return result


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    logger.info("Received startup idea: %r", request.startup_idea)
    try:
        result = analyze_startup(request.startup_idea)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — surface real errors to the caller
        logger.exception("Analysis pipeline failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    logger.info("Analysis %s complete in %.1fs", result["analysis_id"], result["elapsed_seconds"])
    return result
