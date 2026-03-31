"""
Pinecone-backed retriever for the travel RAG pipeline.

Two responsibilities:
1. Ingestion — embed all hotel/flight records and upsert into Pinecone
2. Search   — embed a TravelIntent query and retrieve top-k matches
"""

import json
import os
from typing import Optional

from pinecone import Pinecone, ServerlessSpec

from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from app.embeddings import embed_text, embed_texts, record_to_text, intent_to_query
from app.models import TravelIntent


# ---------------------------------------------------------------------------
# Pinecone client + index setup
# ---------------------------------------------------------------------------
DIMENSION = 384  # all-MiniLM-L6-v2 output dimension


def get_pinecone_client() -> Pinecone:
    """Create and return a Pinecone client."""
    return Pinecone(api_key=PINECONE_API_KEY)


def get_or_create_index(pc: Pinecone) -> object:
    """
    Return the Pinecone index. Create it if it does not exist.
    Uses the free-tier serverless spec (AWS us-east-1).
    """
    existing_indexes = [idx.name for idx in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return pc.Index(PINECONE_INDEX_NAME)


# ---------------------------------------------------------------------------
# Ingestion — load records into Pinecone
# ---------------------------------------------------------------------------
BATCH_SIZE = 100


def ingest_records(records: list[dict], batch_size: int = BATCH_SIZE) -> int:
    """
    Embed all records and upsert them into Pinecone in batches.
    Returns the total number of vectors upserted.
    """
    pc = get_pinecone_client()
    index = get_or_create_index(pc)

    # Convert records to natural-language descriptions
    texts = [record_to_text(r) for r in records]

    # Embed all texts in one batch call
    print(f"Embedding {len(texts)} records...")
    vectors = embed_texts(texts)

    # Upsert in batches to avoid hitting API limits
    total_upserted = 0
    for i in range(0, len(records), batch_size):
        batch_end = min(i + batch_size, len(records))
        batch_vectors = []

        for j in range(i, batch_end):
            record = records[j]
            metadata = {
                "type": record["type"],
                "text": texts[j][:500],  # Pinecone metadata limit
            }

            # Add type-specific metadata for filtering
            if record["type"] == "hotel":
                metadata.update({
                    "destination": record["destination"],
                    "vibe": record["vibe"],
                    "stars": record["stars"],
                    "price_per_night": record["price_per_night"],
                    "rating": record["rating"],
                    "name": record["name"],
                    "amenities": ",".join(record.get("amenities", [])),
                })
            elif record["type"] == "flight":
                metadata.update({
                    "destination": record["destination"],
                    "destination_vibe": record.get("destination_vibe", ""),
                    "origin": record.get("origin", ""),
                    "airline": record["airline"],
                    "cabin_class": record["cabin_class"],
                    "price": record["price"],
                    "departure_date": record.get("departure_date", ""),
                    "duration_hours": record.get("duration_hours", 0),
                    "stops": record.get("stops", 0),
                    "rating": record["rating"],
                })

            batch_vectors.append({
                "id": record["id"],
                "values": vectors[j],
                "metadata": metadata,
            })

        index.upsert(vectors=batch_vectors)
        total_upserted += len(batch_vectors)
        print(f"  Upserted {total_upserted}/{len(records)}")

    return total_upserted


# ---------------------------------------------------------------------------
# Search — retrieve matching hotels and flights
# ---------------------------------------------------------------------------
def _build_filter(
    intent: TravelIntent,
    record_type: str,
) -> dict:
    """
    Build a Pinecone metadata filter from the extracted intent.
    Only adds filter conditions for fields that are not None.
    """
    conditions = [{"type": {"$eq": record_type}}]

    # Vibe filter
    vibe_field = "vibe" if record_type == "hotel" else "destination_vibe"
    if intent.vibe:
        conditions.append({vibe_field: {"$eq": intent.vibe}})

    # Budget filter
    if intent.budget_per_person is not None:
        price_field = "price_per_night" if record_type == "hotel" else "price"
        conditions.append({price_field: {"$lte": intent.budget_per_person}})

    # Combine conditions
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def search(
    intent: TravelIntent,
    top_k: int = 5,
) -> dict:
    """
    Search Pinecone for hotels and flights matching the travel intent.

    Returns:
        {
            "hotels": [{"id": ..., "score": ..., "metadata": {...}}, ...],
            "flights": [{"id": ..., "score": ..., "metadata": {...}}, ...],
        }
    """
    pc = get_pinecone_client()
    index = get_or_create_index(pc)

    # Convert intent to a query string, then to a vector
    query_text = intent_to_query(intent)
    query_vector = embed_text(query_text)

    # Search for hotels
    hotel_filter = _build_filter(intent, "hotel")
    hotel_results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=hotel_filter,
    )

    # Search for flights
    flight_filter = _build_filter(intent, "flight")
    flight_results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=flight_filter,
    )

    return {
        "hotels": [
            {"id": m.id, "score": m.score, "metadata": m.metadata}
            for m in hotel_results.matches
        ],
        "flights": [
            {"id": m.id, "score": m.score, "metadata": m.metadata}
            for m in flight_results.matches
        ],
    }
