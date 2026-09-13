"""
Real web search, backed by Tavily (the search API Strands' own tools
package and AWS's Strands blog posts use for exactly this purpose:
letting agents pull current market/competitor/news information instead
of guessing from the model's training data).

We don't reimplement search — strands_tools already ships a
production-quality, well-maintained Tavily tool. We just re-export it
so every agent module imports it from one place, and we fail loudly at
import time if TAVILY_API_KEY isn't configured (via backend.config).
"""
from backend import config  # noqa: F401  (ensures env vars are validated/set first)
from strands_tools.tavily import tavily_search

__all__ = ["tavily_search"]
