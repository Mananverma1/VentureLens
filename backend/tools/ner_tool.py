"""
Entity-extraction tool for the Competitor Agent.

Uses dslim/bert-base-NER — a real, dedicated NER model — run locally via
the Transformers pipeline, exactly as named in the project plan. Used to
pull companies/orgs/people/locations out of raw research text (e.g. web
search results) so downstream agents get structured entities instead of
having to re-read prose.
"""
from functools import lru_cache

from strands import tool

from backend import config


@lru_cache(maxsize=1)
def _get_pipeline():
    from transformers import pipeline

    return pipeline(
        "ner",
        model=config.NER_MODEL_ID,
        tokenizer=config.NER_MODEL_ID,
        aggregation_strategy="simple",
    )


@tool
def extract_entities(text: str) -> dict:
    """
    Extract named entities (organizations, people, locations, misc) from
    a block of text using dslim/bert-base-NER.

    Args:
        text: The raw text to scan for entities (e.g. a web search result
            or article excerpt).

    Returns:
        A dict listing each entity found, its type, and a confidence
        score, plus a deduplicated list of organizations (useful for
        spotting named competitors).
    """
    if not text or not text.strip():
        return {
            "status": "error",
            "content": [{"text": "No text provided to extract_entities."}],
        }

    ner = _get_pipeline()
    raw_entities = ner(text)

    entities = []
    organizations = set()
    for ent in raw_entities:
        group = ent.get("entity_group", ent.get("entity", "MISC"))
        word = ent["word"]
        entities.append({
            "text": word,
            "type": group,
            "confidence": round(float(ent["score"]), 4),
        })
        if group == "ORG":
            organizations.add(word)

    summary = (
        f"Found {len(entities)} entities "
        f"({len(organizations)} distinct organizations)."
    )

    return {
        "status": "success",
        "content": [{"text": summary}],
        "entities": entities,
        "organizations": sorted(organizations),
        "summary": summary,
    }
