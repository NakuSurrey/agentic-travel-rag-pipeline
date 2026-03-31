"""
Embedding utilities using sentence-transformers (runs locally, free).
Converts travel records and queries into dense vectors for Pinecone.
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """Embed a single text string."""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of text strings."""
    model = get_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=True).tolist()


def record_to_text(record: dict) -> str:
    """
    Convert a hotel or flight record into a natural-language description
    suitable for embedding.
    """
    if record["type"] == "hotel":
        amenities_str = ", ".join(record.get("amenities", []))
        return (
            f"{record['name']} — a {record['stars']}-star {record['vibe']} hotel in "
            f"{record['destination']}. ${record['price_per_night']}/night. "
            f"Rating: {record['rating']}/5. Amenities: {amenities_str}. "
            f"Available {record['available_from']} to {record['available_to']}."
        )
    elif record["type"] == "flight":
        stops_str = "nonstop" if record["stops"] == 0 else f"{record['stops']} stop(s)"
        return (
            f"{record['airline']} flight from {record['origin']} to "
            f"{record['destination']} ({record['destination_vibe']} destination). "
            f"{record['cabin_class'].replace('_', ' ').title()} class — ${record['price']}. "
            f"Departs {record['departure_date']}, {record['duration_hours']}h, {stops_str}. "
            f"Rating: {record['rating']}/5."
        )
    else:
        return str(record)


def intent_to_query(intent) -> str:
    """
    Convert a TravelIntent into a natural-language query string
    for vector similarity search.
    """
    parts = []
    if intent.vibe:
        parts.append(f"{intent.vibe} destination")
    if intent.destination:
        parts.append(f"in or near {intent.destination}")
    if intent.budget_per_person:
        parts.append(f"under ${intent.budget_per_person} per person")
    if intent.check_in and intent.check_out:
        parts.append(f"from {intent.check_in} to {intent.check_out}")
    if intent.amenities:
        parts.append(f"with {', '.join(intent.amenities)}")
    return " ".join(parts) if parts else "travel destination"
