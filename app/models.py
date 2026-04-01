"""Pydantic models for request/response schemas and internal data structures."""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Travel intent extracted from group chat
# ---------------------------------------------------------------------------
class TravelIntent(BaseModel):
    """Structured travel entities parsed from unstructured chat data."""

    destination: Optional[str] = Field(None, description="Preferred destination or region")
    vibe: Optional[str] = Field(
        None,
        description="Destination vibe category: beach, mountain, city, adventure, or cultural",
    )
    budget_per_person: Optional[float] = Field(None, description="Max budget per person in USD")
    check_in: Optional[str] = Field(None, description="Desired check-in / departure date (YYYY-MM-DD)")
    check_out: Optional[str] = Field(None, description="Desired check-out / return date (YYYY-MM-DD)")
    group_size: Optional[int] = Field(None, description="Number of travelers")
    amenities: list[str] = Field(default_factory=list, description="Desired amenities or preferences")
    notes: Optional[str] = Field(None, description="Any extra context from the conversation")


# ---------------------------------------------------------------------------
# API schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    """Incoming request with raw group chat messages."""

    chat_id: Optional[str] = None
    messages: list[dict] = Field(..., description="List of {role, content} message dicts")
    top_k: int = Field(5, description="Number of results to return per category")


class ItineraryHotel(BaseModel):
    id: str
    name: str
    destination: str
    vibe: str
    stars: int
    price_per_night: float
    amenities: list[str]
    rating: float
    score: float = Field(description="Relevance score from vector search")


class ItineraryFlight(BaseModel):
    id: str
    airline: str
    origin: str
    destination: str
    cabin_class: str
    price: float
    departure_date: str
    duration_hours: float
    stops: int
    rating: float
    score: float = Field(description="Relevance score from vector search")


class ItineraryResponse(BaseModel):
    """Final itinerary response returned by the API."""

    chat_id: Optional[str]
    extracted_intent: TravelIntent
    recommended_hotels: list[ItineraryHotel]
    recommended_flights: list[ItineraryFlight]
    summary: str = Field("", description="LLM-generated friendly travel recommendation")
    processing_time_ms: float
