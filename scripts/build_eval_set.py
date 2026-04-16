"""
Build the retrieval evaluation set from real hotel and flight data.

Reads hotels.json and flights.json, creates 25 test queries with
programmatically determined ground truth expected IDs. Saves the
result as data/eval_queries.json.

Ground truth is built by applying the EXACT same filter logic the
retriever uses — so expected_ids are mathematically correct, not
guesses.
"""

import json
import os


# ---------------------------------------------------------------------------
# paths — pointing to the data folder one level up from scripts/
# ---------------------------------------------------------------------------
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
HOTELS_PATH = os.path.join(DATA_DIR, "hotels.json")
FLIGHTS_PATH = os.path.join(DATA_DIR, "flights.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "eval_queries.json")


def load_data():
    """Load hotel and flight records from JSON files."""
    with open(HOTELS_PATH, "r") as f:
        hotels = json.load(f)
    with open(FLIGHTS_PATH, "r") as f:
        flights = json.load(f)
    return hotels, flights


def filter_hotels(hotels, destination=None, vibe=None, max_price=None, min_stars=None, amenity=None):
    """
    Filter hotels using the same logic the retriever's metadata filter uses.
    Returns list of matching hotel IDs.
    """
    results = []
    for h in hotels:
        # destination match — case-insensitive
        if destination and h["destination"].lower() != destination.lower():
            continue
        # vibe match
        if vibe and h["vibe"].lower() != vibe.lower():
            continue
        # budget filter — same as retriever: price_per_night <= max_price
        if max_price is not None and h["price_per_night"] > max_price:
            continue
        # star filter — not used by retriever, but useful for ground truth
        if min_stars is not None and h["stars"] < min_stars:
            continue
        # amenity filter — check if amenity is in the hotel's amenity list
        if amenity and amenity.lower() not in [a.lower() for a in h.get("amenities", [])]:
            continue
        results.append(h["id"])
    return results


def filter_flights(flights, destination=None, vibe=None, max_price=None, cabin_class=None):
    """
    Filter flights using the same logic the retriever's metadata filter uses.
    Returns list of matching flight IDs.
    """
    results = []
    for f in flights:
        # destination match — case-insensitive
        if destination and f["destination"].lower() != destination.lower():
            continue
        # vibe match — flights use destination_vibe field
        if vibe and f.get("destination_vibe", "").lower() != vibe.lower():
            continue
        # budget filter — same as retriever: price <= max_price
        if max_price is not None and f["price"] > max_price:
            continue
        # cabin class filter — not used by retriever, but useful for specificity
        if cabin_class and f["cabin_class"].lower() != cabin_class.lower():
            continue
        results.append(f["id"])
    return results


def build_eval_queries(hotels, flights):
    """
    Build 25 evaluation queries covering different combinations of:
    - vibe types (beach, mountain, city, adventure, cultural)
    - specific destinations
    - budget constraints
    - amenity preferences
    - broad vs narrow queries

    Each query contains:
    - query_id: unique identifier
    - description: human-readable description of what we are testing
    - intent: the TravelIntent fields (same shape the retriever expects)
    - expected_hotel_ids: hotels that SHOULD match based on exact filters
    - expected_flight_ids: flights that SHOULD match based on exact filters
    """
    queries = []

    # -----------------------------------------------------------------------
    # GROUP 1: Single vibe, no budget filter (5 queries — one per vibe)
    # tests whether vector search + vibe filter returns correct vibe
    # -----------------------------------------------------------------------
    vibes = ["beach", "mountain", "city", "adventure", "cultural"]
    for vibe in vibes:
        hotel_ids = filter_hotels(hotels, vibe=vibe)
        flight_ids = filter_flights(flights, vibe=vibe)
        queries.append({
            "query_id": f"vibe-{vibe}",
            "description": f"{vibe} destinations — no budget constraint — tests vibe filter accuracy",
            "intent": {
                "destination": None,
                "vibe": vibe,
                "budget_per_person": None,
                "check_in": None,
                "check_out": None,
                "group_size": None,
                "amenities": [],
                "notes": None,
            },
            "expected_hotel_ids": hotel_ids,
            "expected_flight_ids": flight_ids,
        })

    # -----------------------------------------------------------------------
    # GROUP 2: Specific destination + vibe (5 queries)
    # tests whether adding a destination narrows results correctly
    # -----------------------------------------------------------------------
    destination_tests = [
        ("Cancun", "beach"),
        ("Zermatt", "mountain"),
        ("Tokyo", "city"),
        ("Costa Rica", "adventure"),
        ("Kyoto", "cultural"),
    ]
    for dest, vibe in destination_tests:
        hotel_ids = filter_hotels(hotels, destination=dest, vibe=vibe)
        flight_ids = filter_flights(flights, destination=dest, vibe=vibe)
        queries.append({
            "query_id": f"dest-{dest.lower().replace(' ', '-')}",
            "description": f"{vibe} hotels and flights in {dest} — tests destination + vibe combo",
            "intent": {
                "destination": dest,
                "vibe": vibe,
                "budget_per_person": None,
                "check_in": None,
                "check_out": None,
                "group_size": None,
                "amenities": [],
                "notes": None,
            },
            "expected_hotel_ids": hotel_ids,
            "expected_flight_ids": flight_ids,
        })

    # -----------------------------------------------------------------------
    # GROUP 3: Vibe + budget constraint (5 queries)
    # tests whether budget filter correctly caps prices
    # -----------------------------------------------------------------------
    budget_tests = [
        ("beach", 150),
        ("mountain", 200),
        ("city", 100),
        ("adventure", 300),
        ("cultural", 250),
    ]
    for vibe, budget in budget_tests:
        hotel_ids = filter_hotels(hotels, vibe=vibe, max_price=budget)
        flight_ids = filter_flights(flights, vibe=vibe, max_price=budget)
        queries.append({
            "query_id": f"budget-{vibe}-{budget}",
            "description": f"{vibe} under ${budget} — tests vibe + budget filter together",
            "intent": {
                "destination": None,
                "vibe": vibe,
                "budget_per_person": budget,
                "check_in": None,
                "check_out": None,
                "group_size": None,
                "amenities": [],
                "notes": None,
            },
            "expected_hotel_ids": hotel_ids,
            "expected_flight_ids": flight_ids,
        })

    # -----------------------------------------------------------------------
    # GROUP 4: Destination + budget (5 queries)
    # tests the tightest filter combination the retriever supports
    # -----------------------------------------------------------------------
    dest_budget_tests = [
        ("Bali", "beach", 200),
        ("Banff", "mountain", 300),
        ("Barcelona", "city", 250),
        ("Reykjavik", "adventure", 400),
        ("Florence", "cultural", 180),
    ]
    for dest, vibe, budget in dest_budget_tests:
        hotel_ids = filter_hotels(hotels, destination=dest, vibe=vibe, max_price=budget)
        flight_ids = filter_flights(flights, destination=dest, vibe=vibe, max_price=budget)
        queries.append({
            "query_id": f"tight-{dest.lower().replace(' ', '-')}-{budget}",
            "description": f"{vibe} in {dest} under ${budget} — tightest filter combo",
            "intent": {
                "destination": dest,
                "vibe": vibe,
                "budget_per_person": budget,
                "check_in": None,
                "check_out": None,
                "group_size": None,
                "amenities": [],
                "notes": None,
            },
            "expected_hotel_ids": hotel_ids,
            "expected_flight_ids": flight_ids,
        })

    # -----------------------------------------------------------------------
    # GROUP 5: Edge cases (5 queries)
    # tests how the system handles broad, narrow, and empty result sets
    # -----------------------------------------------------------------------

    # 5a — very broad: no vibe, no destination, no budget
    all_hotel_ids = [h["id"] for h in hotels]
    all_flight_ids = [f["id"] for f in flights]
    queries.append({
        "query_id": "edge-broad",
        "description": "no filters at all — everything is relevant — tests baseline ranking",
        "intent": {
            "destination": None,
            "vibe": None,
            "budget_per_person": None,
            "check_in": None,
            "check_out": None,
            "group_size": None,
            "amenities": [],
            "notes": None,
        },
        "expected_hotel_ids": all_hotel_ids,
        "expected_flight_ids": all_flight_ids,
    })

    # 5b — very tight budget: beach under $60
    hotel_ids = filter_hotels(hotels, vibe="beach", max_price=60)
    flight_ids = filter_flights(flights, vibe="beach", max_price=60)
    queries.append({
        "query_id": "edge-tight-budget",
        "description": "beach under $60 — very few results expected — tests sparse retrieval",
        "intent": {
            "destination": None,
            "vibe": "beach",
            "budget_per_person": 60,
            "check_in": None,
            "check_out": None,
            "group_size": None,
            "amenities": [],
            "notes": None,
        },
        "expected_hotel_ids": hotel_ids,
        "expected_flight_ids": flight_ids,
    })

    # 5c — luxury: mountain, high budget
    hotel_ids = filter_hotels(hotels, vibe="mountain", max_price=1000)
    flight_ids = filter_flights(flights, vibe="mountain", max_price=1000)
    queries.append({
        "query_id": "edge-luxury-mountain",
        "description": "mountain under $1000 — generous budget — tests whether ranking favors quality",
        "intent": {
            "destination": None,
            "vibe": "mountain",
            "budget_per_person": 1000,
            "check_in": None,
            "check_out": None,
            "group_size": None,
            "amenities": [],
            "notes": None,
        },
        "expected_hotel_ids": hotel_ids,
        "expected_flight_ids": flight_ids,
    })

    # 5d — specific destination, no vibe
    hotel_ids = filter_hotels(hotels, destination="Paris")
    flight_ids = filter_flights(flights, destination="Paris")
    queries.append({
        "query_id": "edge-dest-only",
        "description": "Paris only, no vibe — tests destination-only search without vibe filter",
        "intent": {
            "destination": "Paris",
            "vibe": None,
            "budget_per_person": None,
            "check_in": None,
            "check_out": None,
            "group_size": None,
            "amenities": [],
            "notes": None,
        },
        "expected_hotel_ids": hotel_ids,
        "expected_flight_ids": flight_ids,
    })

    # 5e — budget only, no vibe, no destination
    hotel_ids = filter_hotels(hotels, max_price=80)
    flight_ids = filter_flights(flights, max_price=80)
    queries.append({
        "query_id": "edge-budget-only",
        "description": "under $80, no vibe or destination — tests budget-only filtering",
        "intent": {
            "destination": None,
            "vibe": None,
            "budget_per_person": 80,
            "check_in": None,
            "check_out": None,
            "group_size": None,
            "amenities": [],
            "notes": None,
        },
        "expected_hotel_ids": hotel_ids,
        "expected_flight_ids": flight_ids,
    })

    return queries


def main():
    print("Loading hotel and flight data...")
    hotels, flights = load_data()
    print(f"  Loaded {len(hotels)} hotels, {len(flights)} flights")

    print("\nBuilding evaluation queries...")
    queries = build_eval_queries(hotels, flights)

    # show summary for each query
    print(f"\n  Built {len(queries)} evaluation queries:\n")
    for q in queries:
        h_count = len(q["expected_hotel_ids"])
        f_count = len(q["expected_flight_ids"])
        print(f"  {q['query_id']:30s} — hotels: {h_count:5d} | flights: {f_count:5d} — {q['description']}")

    # save to JSON
    with open(OUTPUT_PATH, "w") as f:
        json.dump(queries, f, indent=2)
    print(f"\nSaved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
