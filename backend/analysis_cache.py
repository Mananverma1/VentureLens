"""Small persistent cache for completed startup analyses."""
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


CACHE_PATH = Path(os.getenv(
    "VENTURELENS_CACHE_PATH",
    str(Path(__file__).resolve().parent / ".analysis_cache.json"),
))


def canonicalize_idea(startup_idea: str) -> str:
    """Normalize whitespace so equivalent submissions share one cache key."""
    return " ".join(startup_idea.split())


def analysis_id(startup_idea: str) -> str:
    """Return a stable identifier for one canonical startup idea."""
    digest = hashlib.sha256(canonicalize_idea(startup_idea).lower().encode("utf-8"))
    return digest.hexdigest()[:16]


def get_cached(startup_idea: str) -> dict[str, Any] | None:
    if not CACHE_PATH.exists():
        return None
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as cache_file:
            cached = json.load(cache_file)
    except (OSError, json.JSONDecodeError):
        return None
    return cached.get(analysis_id(startup_idea))


def get_latest() -> dict[str, Any] | None:
    if not CACHE_PATH.exists():
        return None
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as cache_file:
            cached = json.load(cache_file)
    except (OSError, json.JSONDecodeError):
        return None
    return next(reversed(cached.values()), None)


def save_cached(startup_idea: str, result: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cached: dict[str, Any] = {}
    if CACHE_PATH.exists():
        try:
            with CACHE_PATH.open("r", encoding="utf-8") as cache_file:
                cached = json.load(cache_file)
        except (OSError, json.JSONDecodeError):
            cached = {}

    cached[analysis_id(startup_idea)] = result
    fd, temporary_path = tempfile.mkstemp(
        prefix="venturelens-cache-", suffix=".json", dir=CACHE_PATH.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as cache_file:
            json.dump(cached, cache_file, ensure_ascii=False, indent=2)
        os.replace(temporary_path, CACHE_PATH)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)