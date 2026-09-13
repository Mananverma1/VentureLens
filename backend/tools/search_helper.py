"""
Synchronous Tavily search helper.

Calls the Tavily REST API directly with requests (no async) so it works
reliably inside any execution context (uvicorn, threads, CLI).
"""
import logging

import requests

from backend import config

logger = logging.getLogger("venturelens")

TAVILY_URL = "https://api.tavily.com/search"


def search(query: str, max_results: int = 3) -> str:
    """
    Run a Tavily search and return a plain-text summary of the top
    results (title + snippet + source URL), ready to paste into a prompt.
    Returns a fallback string on any error so the pipeline never crashes.
    """
    try:
        resp = requests.post(
            TAVILY_URL,
            json={
                "api_key": config.TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": False,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Tavily search failed for query %r: %s", query, exc)
        return "Search unavailable."

    results = data.get("results", [])
    if not results:
        return "No search results found."

    lines = []
    for r in results:
        title = r.get("title", "")
        content = r.get("content", "")[:400]
        url = r.get("url", "")
        lines.append(f"[{title}]\n{content}\n(source: {url})")

    return "\n\n".join(lines)
