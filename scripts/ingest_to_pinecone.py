"""
One-time script: Load all hotel + flight records into Pinecone.

Run this ONCE before starting the FastAPI server:
    python -m scripts.ingest_to_pinecone

It reads data/all_records.json, embeds each record, and upserts
the vectors + metadata into the Pinecone index.
"""

import json
import os
import time

# Ensure the project root is importable
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.retriever import ingest_records


def main():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "all_records.json")

    print(f"Loading records from {data_path}...")
    with open(data_path, "r") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records.")
    print("Starting ingestion into Pinecone...")

    start = time.time()
    total = ingest_records(records)
    elapsed = time.time() - start

    print(f"\nDone! Upserted {total} vectors in {elapsed:.1f} seconds.")


if __name__ == "__main__":
    main()
