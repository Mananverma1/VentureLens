"""
Central configuration for VentureLens.

Loads every credential from environment variables (via .env). Nothing here
is hard-coded, and nothing here is a placeholder that silently "works" —
missing required config raises immediately so you find out at startup,
not three agents deep into a run.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value or value.strip() == "":
        raise ValueError(
            f"{name} is not set. Copy .env.example to .env and fill in a real "
            f"value for {name}."
        )
    return value


# --- Required credentials ---
HF_TOKEN = os.getenv("HF_TOKEN", "")          # kept for backward compat, optional now
GROQ_API_KEY = _require("GROQ_API_KEY")
TAVILY_API_KEY = _require("TAVILY_API_KEY")

# --- Model selection ---
# LiteLLM format: "groq/<model>", "huggingface/<org>/<model>", etc.
MODEL_ID = os.getenv("MODEL_ID", "groq/llama-3.3-70b-versatile")
HF_PROVIDER = os.getenv("HF_PROVIDER", "").strip()  # optional, only used for HF models

# Backward-compat alias used by hf_model.py
HF_MODEL_ID = MODEL_ID

# --- Local specialist models (run via transformers, no extra API/token needed) ---
SENTIMENT_MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"
NER_MODEL_ID = "dslim/bert-base-NER"

# Expose keys to env so LiteLLM and strands_tools pick them up automatically
os.environ.setdefault("GROQ_API_KEY", GROQ_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", TAVILY_API_KEY)
if HF_TOKEN:
    os.environ.setdefault("HF_TOKEN", HF_TOKEN)
    os.environ.setdefault("HUGGINGFACE_API_KEY", HF_TOKEN)
