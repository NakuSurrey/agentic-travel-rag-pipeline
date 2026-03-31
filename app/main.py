"""
FastAPI server — the single entry point for the Travel RAG pipeline.

Receives group chat messages, extracts travel intent, searches the
vector database for matching hotels and flights, generates a friendly
itinerary summary, and returns the full result as JSON.
"""

import time
import hashlib
import json

from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import APP_API_KEY, HOST, PORT
from app.models import (
    ChatRequest,
    ItineraryResponse,
    ItineraryHotel,
    ItineraryFlight,
    TravelIntent,
)
from app.intent_extractor import extract_intent
from app.retriever import search
from app.itinerary_generator import generate_itinerary


# ---------------------------------------------------------------------------
# App + auth setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Travel RAG API",
    version="1.0.0",
    description="Agentic travel planning pipeline: intent extraction → RAG search → itinerary generation",
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Security(api_key_header)) -> str:
    """Validate the API key from the request header."""
    if not APP_API_KEY:
        return "no-auth"
    if key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return key


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter
# ---------------------------------------------------------------------------
_request_log: dict[str, list[float]] = {}
RATE_LIMIT = 50
RATE_WINDOW = 60  # seconds


def _check_rate_limit(api_key: str) -> None:
    """Block the request if this client has exceeded 50 requests in 60 seconds."""
    now = time.time()
    timestamps = _request_log.get(api_key, [])
    timestamps = [t for t in timestamps if now - t < RATE_WINDOW]
    timestamps.append(now)
    _request_log[api_key] = timestamps
    if len(timestamps) > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
        )


# ---------------------------------------------------------------------------
# Caching helper
# ---------------------------------------------------------------------------
def _make_cache_key(messages: list[dict]) -> str:
    """Create a SHA-256 hash from the messages list for cache lookup."""
    raw = json.dumps(messages, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


_result_cache: dict[str, dict] = {}
MAX_CACHE_SIZE = 128


# ---------------------------------------------------------------------------
# Result builders — convert raw Pinecone matches to Pydantic models
# ---------------------------------------------------------------------------
def _build_hotel(match: dict) -> ItineraryHotel:
    """Convert a single Pinecone hotel match into an ItineraryHotel model."""
    m = match["metadata"]
    amenities_raw = m.get("amenities", "")
    amenities = amenities_raw.split(",") if amenities_raw else []
    return ItineraryHotel(
        id=match["id"],
        name=m.get("name", "Unknown"),
        destination=m.get("destination", "Unknown"),
        vibe=m.get("vibe", "unknown"),
        stars=int(m.get("stars", 0)),
        price_per_night=float(m.get("price_per_night", 0)),
        amenities=amenities,
        rating=float(m.get("rating", 0)),
        score=round(match["score"], 4),
    )


def _build_flight(match: dict) -> ItineraryFlight:
    """Convert a single Pinecone flight match into an ItineraryFlight model."""
    m = match["metadata"]
    return ItineraryFlight(
        id=match["id"],
        airline=m.get("airline", "Unknown"),
        origin=m.get("origin", "Unknown"),
        destination=m.get("destination", "Unknown"),
        cabin_class=m.get("cabin_class", "economy"),
        price=float(m.get("price", 0)),
        departure_date=m.get("departure_date", "TBD"),
        duration_hours=float(m.get("duration_hours", 0)),
        stops=int(m.get("stops", 0)),
        rating=float(m.get("rating", 0)),
        score=round(match["score"], 4),
    )


# ---------------------------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------------------------
@app.post("/api/v1/plan-trip", response_model=ItineraryResponse)
def plan_trip(
    request: ChatRequest,
    api_key: str = Security(verify_api_key),
) -> ItineraryResponse:
    """
    Full pipeline: extract intent → search Pinecone → generate itinerary.
    """
    # --- Rate limit ---
    _check_rate_limit(api_key)

    # --- Check cache ---
    cache_key = _make_cache_key(request.messages)
    if cache_key in _result_cache:
        return ItineraryResponse(**_result_cache[cache_key])

    # --- Timer start ---
    start = time.time()

    # --- Step 1: Extract intent ---
    try:
        intent = extract_intent(request.messages)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Intent extraction failed: {e}",
        )

    # --- Step 2: Search Pinecone ---
    try:
        results = search(intent, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Search service unavailable: {e}",
        )

    # --- Step 3: Generate itinerary ---
    try:
        summary = generate_itinerary(intent, results)
    except Exception:
        summary = "Itinerary summary could not be generated at this time."

    # --- Build response ---
    hotels = [_build_hotel(h) for h in results.get("hotels", [])]
    flights = [_build_flight(f) for f in results.get("flights", [])]

    elapsed_ms = round((time.time() - start) * 1000, 2)

    response_data = {
        "chat_id": request.chat_id,
        "extracted_intent": intent,
        "recommended_hotels": hotels,
        "recommended_flights": flights,
        "summary": summary,
        "processing_time_ms": elapsed_ms,
    }

    # --- Store in cache ---
    if len(_result_cache) >= MAX_CACHE_SIZE:
        _result_cache.clear()
    _result_cache[cache_key] = response_data

    return ItineraryResponse(**response_data)


# ---------------------------------------------------------------------------
# Run server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
