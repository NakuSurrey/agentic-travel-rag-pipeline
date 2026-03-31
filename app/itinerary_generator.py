"""
Itinerary generator — passes extracted intent and RAG search results
to the LLM, which writes a friendly, human-readable travel summary.

Input:  TravelIntent + raw Pinecone search results (hotels & flights)
Output: A plain-text travel recommendation string
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY, LLM_MODEL
from app.models import TravelIntent


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a friendly travel agent. The user's group has these preferences:\n"
        "{intent_summary}\n\n"
        "Based on a database search, here are the top matching results.\n\n"
        "HOTELS:\n{hotels_text}\n\n"
        "FLIGHTS:\n{flights_text}\n\n"
        "Write a short, friendly travel recommendation (3-5 paragraphs). "
        "Mention specific hotel names, prices, and flight details from the results. "
        "If no hotels or flights were found, say so politely and suggest broadening "
        "the search criteria. Do NOT invent results that are not listed above."
    ),
    (
        "human",
        "Please write our group's travel itinerary summary."
    ),
])


# ---------------------------------------------------------------------------
# Helper — format search results into readable text
# ---------------------------------------------------------------------------
def _format_hotel(match: dict, rank: int) -> str:
    """Convert a single Pinecone hotel match into a readable line."""
    meta = match["metadata"]
    return (
        f"{rank}. {meta.get('name', 'Unknown')} — "
        f"{meta.get('destination', '?')}, "
        f"{meta.get('stars', '?')}-star, "
        f"${meta.get('price_per_night', '?')}/night, "
        f"vibe: {meta.get('vibe', '?')}, "
        f"rating: {meta.get('rating', '?')}/5, "
        f"amenities: {meta.get('amenities', 'N/A')} "
        f"(match score: {match['score']:.2f})"
    )


def _format_flight(match: dict, rank: int) -> str:
    """Convert a single Pinecone flight match into a readable line."""
    meta = match["metadata"]
    stops_str = "nonstop" if meta.get("stops", 0) == 0 else f"{meta.get('stops')} stop(s)"
    return (
        f"{rank}. {meta.get('airline', 'Unknown')} — "
        f"{meta.get('origin', '?')} to {meta.get('destination', '?')}, "
        f"${meta.get('price', '?')}, "
        f"{meta.get('cabin_class', '?').replace('_', ' ').title()}, "
        f"{meta.get('departure_date', '?')}, "
        f"{meta.get('duration_hours', '?')}h, {stops_str}, "
        f"rating: {meta.get('rating', '?')}/5 "
        f"(match score: {match['score']:.2f})"
    )


def _format_intent(intent: TravelIntent) -> str:
    """Convert TravelIntent into a readable summary for the LLM."""
    parts = []
    if intent.destination:
        parts.append(f"Destination: {intent.destination}")
    if intent.vibe:
        parts.append(f"Vibe: {intent.vibe}")
    if intent.budget_per_person is not None:
        parts.append(f"Budget: ${intent.budget_per_person} per person")
    if intent.check_in:
        parts.append(f"Check-in: {intent.check_in}")
    if intent.check_out:
        parts.append(f"Check-out: {intent.check_out}")
    if intent.group_size is not None:
        parts.append(f"Group size: {intent.group_size}")
    if intent.amenities:
        parts.append(f"Amenities wanted: {', '.join(intent.amenities)}")
    return "\n".join(parts) if parts else "No specific preferences extracted."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_itinerary(
    intent: TravelIntent,
    search_results: dict,
) -> str:
    """
    Generate a friendly travel summary from intent + search results.

    Args:
        intent: The structured TravelIntent extracted from the group chat.
        search_results: Dict with "hotels" and "flights" lists from retriever.search().

    Returns:
        A plain-text travel recommendation string from the LLM.
        Returns a fallback message if no API key is configured.
    """
    # --- Format inputs for the prompt ---
    intent_summary = _format_intent(intent)

    hotels = search_results.get("hotels", [])
    flights = search_results.get("flights", [])

    hotels_text = "\n".join(
        _format_hotel(h, i + 1) for i, h in enumerate(hotels)
    ) if hotels else "No matching hotels found."

    flights_text = "\n".join(
        _format_flight(f, i + 1) for i, f in enumerate(flights)
    ) if flights else "No matching flights found."

    # --- Fallback if no API key ---
    if not GROQ_API_KEY:
        return (
            "Itinerary summary unavailable (no LLM API key configured). "
            "See the raw hotel and flight results in the response."
        )

    # --- Call the LLM ---
    llm = ChatGroq(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0.7,
        max_tokens=1024,
    )

    chain = SUMMARY_PROMPT | llm

    response = chain.invoke({
        "intent_summary": intent_summary,
        "hotels_text": hotels_text,
        "flights_text": flights_text,
    })

    return response.content
