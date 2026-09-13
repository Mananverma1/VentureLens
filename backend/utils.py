"""
Utility helpers for VentureLens.
"""
import logging
import re
import time

from litellm import RateLimitError

logger = logging.getLogger("venturelens")


def run_with_retry(fn, *args, max_retries: int = 5, **kwargs):
    """
    Call fn(*args, **kwargs). If a RateLimitError is raised, parse the
    wait time from the error message, sleep, and retry up to max_retries
    times. Any other exception is re-raised immediately.
    """
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except RateLimitError as exc:
            if attempt == max_retries:
                raise
            # Try to parse suggested wait from the error message
            match = re.search(r"try again in (\d+\.?\d*)", str(exc), re.IGNORECASE)
            wait = float(match.group(1)) + 5 if match else 60
            logger.warning(
                "Rate limit hit (attempt %d/%d). Waiting %.0fs before retry...",
                attempt + 1, max_retries, wait,
            )
            time.sleep(wait)
