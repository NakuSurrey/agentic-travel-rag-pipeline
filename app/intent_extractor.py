"""
Agentic LangChain pipeline to extract structured travel intent
from unstructured group chat messages.

Uses Groq (Llama 3.1 70B) — free tier, fast inference.
Falls back to rule-based extraction when no API key is configured.
"""

import json
import re
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models import TravelIntent
from app.config import GROQ_API_KEY, LLM_MODEL


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a travel-planning assistant. Analyze the group chat below and "
        "extract structured travel intent. Return ONLY valid JSON matching this schema:\n"
        "{schema}\n\n"
        "Rules:\n"
        "- vibe must be one of: beach, mountain, city, adventure, cultural\n"
        "- Dates should be YYYY-MM-DD format. Infer year as 2026 if not stated.\n"
        "- budget_per_person is the per-person max in USD\n"
        "- amenities: list specific preferences mentioned (pool, spa, etc.)\n"
        "- If something is not mentioned, set it to null\n"
        "- Do NOT wrap in markdown code fences"
    ),
    (
        "human",
        "Group chat:\n{chat_text}"
    ),
])

SCHEMA_STR = json.dumps(TravelIntent.model_json_schema(), indent=2)


def _flatten_chat(messages: list[dict]) -> str:
    """Convert list of {user, text} dicts into readable chat transcript."""
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)


# ---------------------------------------------------------------------------
# LLM-based extraction (Groq / Llama 3.1)
# ---------------------------------------------------------------------------
def _extract_with_llm(chat_text: str) -> TravelIntent:
    """Use LangChain + Groq to extract intent via LLM."""
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0,
        max_tokens=1024,
    )
    parser = JsonOutputParser(pydantic_object=TravelIntent)
    chain = EXTRACTION_PROMPT | llm | parser

    result = chain.invoke({"schema": SCHEMA_STR, "chat_text": chat_text})
    return TravelIntent(**result)


# ---------------------------------------------------------------------------
# Rule-based fallback (no API key needed)
# ---------------------------------------------------------------------------
VIBE_KEYWORDS = {
    "beach": ["beach", "beachy", "tropical", "island", "resort", "coast", "ocean", "surf", "sand"],
    "mountain": ["mountain", "hiking", "ski", "alpine", "peaks", "summit", "trail", "elevation"],
    "city": ["city", "urban", "nightlife", "downtown", "metropolitan", "food scene", "restaurants"],
    "adventure": ["adventure", "backpack", "explore", "volcano", "rainforest", "wildlife", "extreme"],
    "cultural": ["cultural", "temple", "museum", "heritage", "historic", "traditional", "market"],
}

DATE_PATTERN = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2})"
    r"|(?:\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)"
    r"|(?:\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:\s*[-–to]+\s*\d{1,2})?\b)"
)

BUDGET_PATTERN = re.compile(r"\$\s?([\d,]+(?:\.\d{2})?)")


def _detect_vibe(text: str) -> Optional[str]:
    text_lower = text.lower()
    scores = {}
    for vibe, keywords in VIBE_KEYWORDS.items():
        scores[vibe] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def _extract_rule_based(chat_text: str) -> TravelIntent:
    """Regex + heuristic extraction — works offline with no API key."""
    budgets = BUDGET_PATTERN.findall(chat_text)
    budget = min(float(b.replace(",", "")) for b in budgets) if budgets else None

    vibe = _detect_vibe(chat_text)

    # Detect amenities
    amenity_keywords = [
        "pool", "spa", "gym", "wifi", "beach access", "mountain view",
        "breakfast", "restaurant", "bar", "parking", "pet friendly",
        "room service", "hot tub", "rooftop",
    ]
    amenities = [a for a in amenity_keywords if a in chat_text.lower()]

    # Count unique users as group size
    lines = chat_text.strip().split("\n")
    users = set()
    for line in lines:
        if ":" in line:
            users.add(line.split(":")[0].strip())
    group_size = len(users) if users else None

    return TravelIntent(
        destination=None,
        vibe=vibe,
        budget_per_person=budget,
        check_in=None,
        check_out=None,
        group_size=group_size,
        amenities=amenities,
        notes="Extracted via rule-based fallback (no LLM API key configured)",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def extract_intent(messages: list[dict]) -> TravelIntent:
    """
    Main entry point: extract travel intent from chat messages.
    Uses LLM if GROQ_API_KEY is set, otherwise falls back to rules.
    """
    chat_text = _flatten_chat(messages)

    if GROQ_API_KEY:
        return _extract_with_llm(chat_text)
    else:
        return _extract_rule_based(chat_text)
