"""
Generate 10,000+ mock hotel and flight records for the travel RAG pipeline.
Outputs JSON files to ../data/
"""

import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DESTINATIONS = {
    "beach": ["Cancun", "Bali", "Maldives", "Phuket", "Maui", "Santorini", "Zanzibar", "Barbados", "Tulum", "Goa"],
    "mountain": ["Aspen", "Zermatt", "Chamonix", "Banff", "Queenstown", "Interlaken", "Cusco", "Patagonia", "Whistler", "Innsbruck"],
    "city": ["Tokyo", "Paris", "New York", "London", "Barcelona", "Dubai", "Singapore", "Rome", "Istanbul", "Bangkok"],
    "adventure": ["Reykjavik", "Queenstown", "Cape Town", "Moab", "Kathmandu", "Patagonia", "Costa Rica", "Marrakech", "Namibia", "Alaska"],
    "cultural": ["Kyoto", "Florence", "Havana", "Jaipur", "Fez", "Luang Prabang", "Oaxaca", "Siem Reap", "Prague", "Athens"],
}

HOTEL_CHAINS = [
    "Marriott", "Hilton", "Hyatt", "Four Seasons", "Ritz-Carlton",
    "Holiday Inn", "Best Western", "Radisson", "Sheraton", "W Hotels",
    "Courtyard", "Hampton Inn", "La Quinta", "Motel 6", "Boutique Stay",
]

AIRLINES = [
    "Delta", "United", "American Airlines", "Southwest", "JetBlue",
    "Emirates", "Qatar Airways", "Singapore Airlines", "Lufthansa",
    "British Airways", "Air France", "ANA", "Cathay Pacific", "Turkish Airlines",
    "Alaska Airlines",
]

AMENITIES = [
    "Free WiFi", "Pool", "Spa", "Gym", "Restaurant", "Bar",
    "Room Service", "Beach Access", "Mountain View", "City View",
    "Breakfast Included", "Airport Shuttle", "Pet Friendly", "Parking",
    "Concierge", "Business Center", "Rooftop Terrace", "Hot Tub",
]

CABIN_CLASSES = ["economy", "premium_economy", "business", "first"]

ORIGIN_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "San Francisco",
    "Miami", "Seattle", "Boston", "Denver", "Atlanta",
    "Dallas", "Washington DC", "Philadelphia", "Phoenix", "Minneapolis",
]


def random_date(start_days=30, end_days=365):
    """Return a random future date string."""
    base = datetime(2026, 1, 1)
    delta = timedelta(days=random.randint(start_days, end_days))
    return (base + delta).strftime("%Y-%m-%d")


def generate_hotels(n: int = 5500) -> list[dict]:
    """Generate n hotel records."""
    hotels = []
    for i in range(n):
        vibe = random.choice(list(DESTINATIONS.keys()))
        city = random.choice(DESTINATIONS[vibe])
        stars = random.choices([2, 3, 4, 5], weights=[10, 30, 40, 20])[0]
        base_price = {2: 50, 3: 100, 4: 200, 5: 400}[stars]
        price_per_night = round(base_price * random.uniform(0.7, 1.8), 2)
        num_amenities = random.randint(3, 8)

        hotels.append({
            "id": f"HTL-{i+1:05d}",
            "type": "hotel",
            "name": f"{random.choice(HOTEL_CHAINS)} {city}",
            "destination": city,
            "vibe": vibe,
            "stars": stars,
            "price_per_night": price_per_night,
            "amenities": random.sample(AMENITIES, num_amenities),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "available_from": random_date(30, 180),
            "available_to": random_date(200, 365),
        })
    return hotels


def generate_flights(n: int = 5500) -> list[dict]:
    """Generate n flight records."""
    flights = []
    for i in range(n):
        vibe = random.choice(list(DESTINATIONS.keys()))
        dest = random.choice(DESTINATIONS[vibe])
        origin = random.choice(ORIGIN_CITIES)
        cabin = random.choice(CABIN_CLASSES)
        base = {"economy": 200, "premium_economy": 450, "business": 1200, "first": 3000}[cabin]
        price = round(base * random.uniform(0.6, 2.0), 2)
        dep_date = random_date(14, 300)
        duration_hrs = round(random.uniform(2.0, 18.0), 1)
        stops = random.choices([0, 1, 2], weights=[50, 35, 15])[0]

        flights.append({
            "id": f"FLT-{i+1:05d}",
            "type": "flight",
            "airline": random.choice(AIRLINES),
            "origin": origin,
            "destination": dest,
            "destination_vibe": vibe,
            "cabin_class": cabin,
            "price": price,
            "departure_date": dep_date,
            "duration_hours": duration_hrs,
            "stops": stops,
            "rating": round(random.uniform(3.0, 5.0), 1),
        })
    return flights


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)

    hotels = generate_hotels(5500)
    flights = generate_flights(5500)

    with open(os.path.join(out_dir, "hotels.json"), "w") as f:
        json.dump(hotels, f, indent=2)

    with open(os.path.join(out_dir, "flights.json"), "w") as f:
        json.dump(flights, f, indent=2)

    # Combined records for embedding ingestion
    all_records = hotels + flights
    with open(os.path.join(out_dir, "all_records.json"), "w") as f:
        json.dump(all_records, f, indent=2)

    print(f"Generated {len(hotels)} hotels, {len(flights)} flights ({len(all_records)} total)")


if __name__ == "__main__":
    main()
