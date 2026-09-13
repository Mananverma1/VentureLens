"""
Model factory for VentureLens.

Returns a Strands-compatible LiteLLMModel configured for whichever
provider is set in config.MODEL_ID. Also patches LiteLLM's global
retry settings so rate-limit errors are handled with backoff instead
of crashing the pipeline.
"""
import litellm
from strands.models.litellm import LiteLLMModel

from backend import config

# Automatically retry on rate-limit (429) with exponential backoff.
# This keeps the pipeline alive even on Groq's tight free-tier limits.
litellm.num_retries = 6
litellm.retry_after = 30  # seconds to wait before first retry on 429


def get_hf_model(temperature: float = 0.4, max_tokens: int = 2000) -> LiteLLMModel:
    """
    Build a Strands-compatible model object for the configured provider.
    """
    model_id = config.MODEL_ID

    # For HF models, optionally pin a specific inference provider
    if model_id.startswith("huggingface/") and config.HF_PROVIDER:
        prefix, _, rest = model_id.partition("/")
        model_id = f"{prefix}/{config.HF_PROVIDER}/{rest}"

    # Pick the right API key based on provider prefix
    if model_id.startswith("groq/"):
        api_key = config.GROQ_API_KEY
    else:
        api_key = config.HF_TOKEN or config.GROQ_API_KEY

    return LiteLLMModel(
        client_args={
            "api_key": api_key,
        },
        model_id=model_id,
        params={
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )
