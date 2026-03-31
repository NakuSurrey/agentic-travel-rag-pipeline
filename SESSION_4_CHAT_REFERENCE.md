# SESSION 4 — COMPLETE CHAT REFERENCE
## Phase 3 Completion: FastAPI Server (`main.py`) + File Updates

**Date:** March 31, 2026
**Status:** Phase 3 build complete. All files built and taught. Pending: comprehension check, PHASE_3_REFERENCE.md, GitHub push.

---

## TABLE OF CONTENTS

0. [Complete Session Flow — Every Exchange in Order](#0-complete-session-flow--every-exchange-in-order)
1. [Session Start — Where We Left Off](#1-session-start--where-we-left-off)
2. [What Was Built This Session](#2-what-was-built-this-session)
3. [Pre-Build Teach Explanation](#3-pre-build-teach-explanation)
4. [File Update 1: config.py — Added APP_API_KEY](#4-file-update-1-configpy--added-app_api_key)
5. [File Update 2: .env and .env.example — Added APP_API_KEY](#5-file-update-2-env-and-envexample--added-app_api_key)
6. [File Update 3: models.py — Added summary Field](#6-file-update-3-modelspy--added-summary-field)
7. [File Built: app/main.py — Full Code](#7-file-built-appmainpy--full-code)
8. [Line-by-Line Teach-Through: main.py](#8-line-by-line-teach-through-mainpy)
9. [Q&A and Teaching Discussions](#9-qa-and-teaching-discussions)
10. [Connection Summary — main.py](#10-connection-summary--mainpy)
11. [Full End-to-End Request Flow](#11-full-end-to-end-request-flow)
12. [Cumulative Connection Map (Phase 1 + 2 + 3)](#12-cumulative-connection-map-phase-1--2--3)
13. [Final Project File Tree](#13-final-project-file-tree)
14. [All Code Files — Final State](#14-all-code-files--final-state)
15. [Key Concepts Learned This Session](#15-key-concepts-learned-this-session)
16. [Interview Prep Checkpoints](#16-interview-prep-checkpoints)
17. [What Remains After This Session](#17-what-remains-after-this-session)

---

## 0. Complete Session Flow — Every Exchange in Order

This section captures the EXACT sequence of events, user confirmations, questions, answers, corrections, and comprehension gates in the order they happened. Use this as the "play-by-play" transcript. The later sections organize the same content by topic for easier reference.

### Exchange 1: Discovery Request

**Sean asked:** "please check the reference files and tell me what next need to be built"

**Action taken:** An agent explored all project files, read PHASE_1_REFERENCE.md, PHASE_2_REFERENCE.md, SESSION_3_CHAT_REFERENCE.md, and all code files.

**Result reported to Sean:**
- Phases 1 and 2 fully complete and pushed to GitHub
- Phase 3 partially done: `itinerary_generator.py` built and taught, `main.py` not yet started
- What needs to be built: `app/main.py`, updates to `config.py` (APP_API_KEY), `models.py` (summary field), `.env` / `.env.example`
- Remaining tasks: Swagger UI verification, PHASE_3_REFERENCE.md, GitHub push

### Exchange 2: User Confirmation to Proceed

**Sean said:** "yes please"

**Action:** Proceeded to pre-build teach explanation per the mentorship protocol.

### Exchange 3: Pre-Build Teach Explanation (TEACH FIRST)

Gave the full structured teach-first explanation:
- WHAT `main.py` is (the web server, single entry point)
- WHY it's needed (no module is connected to the internet without it)
- Architecture diagram showing main.py connecting to every module
- What each new piece does (auth, endpoint, error handling, rate limiting, cache)
- WHERE it sits in the codebase (the only outward-facing file)

**Asked Sean:** "Do you understand the role of main.py? Say 'got it' or 'go ahead' when ready."

**Sean confirmed:** "yes i understand the main.py file please proceed"

### Exchange 4: File Update — config.py

Added `APP_API_KEY: str = os.getenv("APP_API_KEY", "")` to config.py. Explained what it does, why it exists, how it connects.

### Exchange 5: File Updates — .env and .env.example

Added `APP_API_KEY=dev-travel-key-2026` to `.env` and `APP_API_KEY=your_api_key_here` to `.env.example`. Explained why two files exist.

### Exchange 6: File Update — models.py

Added `summary: str = Field("", description="...")` to `ItineraryResponse`. Explained why `""` default instead of `Optional[str] = None`.

### Exchange 7: Piece 1 — Imports (line-by-line teach)

Explained all 11 import lines one by one. Each with WHAT/WHY/UNDER THE HOOD/CONNECTS.

**Question asked after Piece 1:** "We import hashlib and json for caching. Walk me through exactly what happens, step by step, when two different clients send the exact same list of chat messages. What does hashlib do? What does json do? Why do we need both?"

**Sean's answer:** "it gets caught in the lru cache. json is the one that creates the string for the hash. so we require both. hashlib does is to convert the text messages into unique [fingerprints]."

**Verdict:** Right track but incomplete — missing step-by-step sequence.

**Follow-up question:** "Walk through what happens to Client B's request at each step: (1) messages arrive — what does json do? (2) we have a string — what does hashlib do? (3) we have a hash — what does lru_cache do? (4) what does Client B get back?"

**Sean's answer:** "json converts them to string and hashlib converts that string to hashcode and the lru cache keeps the record of that string conversion to hash as the second user asks the same thing again"

**Verdict:** Close but one thing off — need to clarify what lru_cache actually stores.

**Follow-up question:** "Which thing does lru_cache actually store and check against — the hash, or the function's full result? (a) See hash, find match, return stored pipeline result without running pipeline? (b) See hash, find match, re-run pipeline but faster?"

**Sean's answer:** "a"

**Verdict:** Correct.

**Comprehension gate — "say it back to me":** "Now say that back to me in your own words — one or two sentences. What does lru_cache actually store, and what does it skip?"

**Sean's final answer:** "lru_cache contains the hash and the full result so it does not run the full function again instead it just gets the stored value"

**Verdict:** CONFIRMED. Moved forward.

### Exchange 8: Piece 2 — App initialization and API key security (line-by-line teach)

Explained `app = FastAPI(...)`, `api_key_header = APIKeyHeader(...)`, `verify_api_key()`, the `if not APP_API_KEY` guard, and the `key != APP_API_KEY` check.

**Question asked after Piece 2:** "Look at `if not APP_API_KEY: return 'no-auth'`. What would happen if we removed that line and a developer runs the server locally without setting APP_API_KEY in .env?"

**Sean's initial answer:** "i don't think this will create any problem because if the request is passing the API key as the header then it will not be checked over here, will be checked in the next if condition. It will show invalid API key."

**Verdict:** Partially correct — got the outcome right (invalid API key) but missed the critical WHY.

**Follow-up teaching:** Walked through the exact comparison:
- `key` = `"some-key-123"` (what client sent)
- `APP_API_KEY` = `""` (empty string — developer forgot)
- `key != APP_API_KEY` becomes `"some-key-123" != ""` which is `True`
- Developer gets rejected even though they did nothing wrong

**Comprehension gate — "say it back":** "What is the purpose of the `if not APP_API_KEY` guard?"

**Sean's final answer:** "this is for local development help in case the developer even though sends the key as the header while sending the request, in case if it is not there or not matches with situation that the developer forgot to add the key in the .env file, the authorization still works and the flow goes through without any hindrance"

**Verdict:** CONFIRMED. Moved forward.

### Exchange 9: Piece 3 — Rate limiting (line-by-line teach)

Explained every line: `_request_log`, `RATE_LIMIT`, `RATE_WINDOW`, `_check_rate_limit()`, `time.time()`, the filtering line, `append`, the count check with 429.

**Question asked after Piece 3:** "Look at `timestamps = [t for t in timestamps if now - t < RATE_WINDOW]`. Why do we need this filtering step? What would go wrong if we removed it and just kept appending timestamps forever?"

**Sean's answer:** "this filtering is required in order to keep only those timestamps which are made in the last 60 second window, basically the request made. We just want last 60 second windows for keeping the timestamps."

**Verdict:** Correct on what it does, but did not answer the second part (what goes wrong without it).

**Follow-up:** "What would go wrong? Think about (1) what happens to len(timestamps) after a few hours, and (2) what happens to server memory after a few days."

**Sean's answer:** "brute force attack"

**Verdict:** Right direction but not specific enough.

**Teaching correction given:** Two specific problems:
1. **False rejections** — after 51 total requests ever (even over hours), len > 50 becomes permanently True. Legitimate users permanently locked out.
2. **Memory leak** — timestamps grow forever, eating memory until server crashes.

**Comprehension gate — "say it back":** "What two problems does the filter line prevent?"

**Sean's final answer:** "preventing the legitimate user to get 429 error because it is a timestamp thing so that even if the timestamp before 60 second has more than 50 requests it doesn't get blocked. And memory leak making the system crashes on appending so many requests."

**Verdict:** CONFIRMED. Both problems nailed. Moved forward.

### Exchange 10: Piece 4 — Cache helper and result builders (line-by-line teach)

Explained `_make_cache_key()`, `json.dumps(sort_keys=True)`, `hashlib.sha256().hexdigest()`, `_result_cache`, `MAX_CACHE_SIZE`, `_build_hotel()`, `_build_flight()`, defensive `.get()`, amenities `split(",")`.

**Question asked after Piece 4:** "In _make_cache_key, we use sort_keys=True. Give me a concrete example: two dictionaries that are logically identical but would produce different cache keys without sort_keys=True."

**Sean's answer:** `{"user": "Alice", "text": "hi"}` and `{"text": "hi", "user": "Alice"}` — "as SHA algorithm makes new string for a unique output it will make two input hash keys uniquely for these two as well without sort_keys=True. So it helps in preventing the duplication."

**Verdict:** CONFIRMED. Correct example, correct reasoning. Moved forward.

### Exchange 11: Piece 5 — The endpoint + server runner (line-by-line teach)

Explained the `@app.post` decorator, `plan_trip` function parameters, rate limit call, cache check, `time.time()` start, all three pipeline steps with try/except, the build response block, cache storage, `return ItineraryResponse(**response_data)`, `if __name__ == "__main__"`, `uvicorn.run()`.

Specifically taught WHY Step 3 uses a fallback string instead of raising HTTPException like Steps 1 and 2. Also taught WHY 502 (not 500) for Groq failures.

**Question asked after Piece 5:** "Step 3 handles errors differently from Steps 1 and 2. Why? What would be the problem if Step 3 also raised HTTPException?"

**Sean's initial answer:** "because at least we want to get the results despite the exception. Now the one wanted as proper itinerary but the words used to make it."

**Verdict:** Right direction but vague.

**Follow-up:** "You said 'at least we want to get the results.' Which results specifically? What does the client still receive even when Step 3 fails?"

**Sean's answer:** "like the words which are used to make the itinerary"

**Verdict:** Incorrect. Confused the summary text with the search results.

**Follow-up teaching:** Listed the three pipeline outputs:
```
Step 1 -> extract_intent()      -> produces: TravelIntent
Step 2 -> search()              -> produces: hotels list + flights list
Step 3 -> generate_itinerary()  -> produces: summary text
```
Asked: "If Step 3 fails, which output does the client lose? And which two does the client still receive?"

**Sean's corrected answer:** "so it should be the hotels and flights list on the basis of the intent"

**Verdict:** Correct.

**Comprehension gate — "say it back":** "Why does Step 3 use a fallback instead of raising an error?"

**Sean's final answer:** "it uses a fallback because it has sense only if it has the intent. There is no use making the error handling complex when the input is not there for that function."

**Corrected framing provided:** Step 3 uses a fallback because the hotels and flights are the real value. If the summary fails, the client still receives all the useful search results. Crashing the entire request just because the friendly text failed would throw away all that useful data.

**Verdict:** CONFIRMED with correction. Moved forward.

### Exchange 12: main.py file written

The complete `app/main.py` (199 lines) was created with all sections: imports, app setup, auth, rate limiter, cache helper, result builders, endpoint, server runner.

### Exchange 13: Post-build explanation

Provided structured post-build explanation:
- WHAT was built (one sentence)
- HOW it works (12-step flow)
- HOW it connects to everything (full connection map with deletion consequences)

### Exchange 14: Comprehension check posed (PENDING)

Three questions were asked:
1. "What does main.py do?" (one or two sentences)
2. "Why does it exist?" (what's missing without it)
3. "How does it connect to the rest of the codebase?" (which files, what order, what it receives)

**Sean did NOT answer these yet.** Instead, Sean requested the comprehensive reference file be created.

### Exchange 15: User requested reference file

**Sean said:** "i would like to create reference markdown file of this whole chat. Whatever changes done or the further things done in this chat add them to a reference markdown file so that it acts as a complete reference notes. Like every code and text exchanges, new ones added, error discussions, like literally everything in this chat, all the code files made, like everyone of them, all the things in detail, nothing to be missed which should have been there as a reference."

**Action:** SESSION_4_CHAT_REFERENCE.md was created.

### Exchange 16: Verification check

**Sean asked:** "does this reference contain everything from the chat? Please make multiple checks."

**Action:** A verification agent cross-checked the file against all session events. Found gaps: missing user confirmations, missing comprehension gates, missing Q&A positioning within build flow.

**Action:** This Section 0 was added to fill all gaps.

---

## 1. Session Start — Where We Left Off

### Completed before this session (Phases 1, 2, and partial Phase 3)

**Phase 1 — Foundation Layer:**

| File | Purpose |
|---|---|
| `app/config.py` | Loads all API keys and settings from `.env` via environment variables |
| `app/models.py` | Defines Pydantic data models: `TravelIntent`, `ChatRequest`, `ItineraryHotel`, `ItineraryFlight`, `ItineraryResponse` |
| `app/intent_extractor.py` | Extracts structured `TravelIntent` from group chat. LLM mode (Groq) + rule-based fallback |
| `app/embeddings.py` | Converts text to 384-dimension vectors. Contains `record_to_text`, `intent_to_query`, `embed_text`, `embed_texts` |
| `app/__init__.py` | Empty file that tells Python `app/` is a package |
| `scripts/generate_mock_data.py` | Generates 11,000 fake hotel + flight records |
| `data/hotels.json` | 5,500 generated hotel records |
| `data/flights.json` | 5,500 generated flight records |
| `data/all_records.json` | Combined hotels + flights |
| `data/sample_chats.json` | 5 example group chats for testing |
| `.env` / `.env.example` | Environment variable files |
| `.gitignore` | Prevents `.env`, `__pycache__`, etc. from being committed |
| `requirements.txt` | All Python dependencies |

**Phase 2 — RAG Retrieval Layer:**

| File | Purpose |
|---|---|
| `app/retriever.py` | Connects to Pinecone. Two jobs: (1) ingest records as vectors, (2) search for matching hotels/flights by similarity |
| `scripts/ingest_to_pinecone.py` | One-time script that loads all 11,000 records into Pinecone |

**Phase 3 (partial — from Session 3):**

| File | Purpose |
|---|---|
| `app/itinerary_generator.py` | Formats search results + generates friendly LLM summary. BUILT and fully taught in Session 3 |

**Not yet built at session start:** `app/main.py`, updates to `config.py`, `models.py`, `.env`, `.env.example`

---

## 2. What Was Built This Session

| Change | File | What was done |
|---|---|---|
| UPDATE | `app/config.py` | Added `APP_API_KEY` variable (line 24) |
| UPDATE | `.env` | Added `APP_API_KEY=dev-travel-key-2026` |
| UPDATE | `.env.example` | Added `APP_API_KEY=your_api_key_here` |
| UPDATE | `app/models.py` | Added `summary` field to `ItineraryResponse` (line 70) |
| NEW FILE | `app/main.py` | Full FastAPI server — endpoint, auth, rate limiting, caching, error handling (199 lines) |

---

## 3. Pre-Build Teach Explanation

### What `main.py` is

The FastAPI web server. The single entry point that outside clients use to talk to the entire pipeline. Before this file, every module (intent_extractor, retriever, itinerary_generator) was standalone Python. None were connected to the internet. No client could call them. `main.py` creates an HTTP endpoint — a URL that a client sends data to and receives data back from.

### Why it is needed

Phases 1 and 2 built the internal engine — extract intent, search vectors, generate summary. But an engine on a shelf is useless. `main.py` is the ignition. It receives a request from the outside world, runs the engine, and sends back the result.

### How it connects to what was already built

```
[External HTTP Client]
      |
      |  POST /api/v1/plan-trip  (sends JSON with chat messages)
      |
      v
+----------------------------------+
|  main.py (FastAPI)               |
|                                  |
|  1. Validate API key             |
|  2. Call intent_extractor -------+--> intent_extractor.py --> config.py, models.py
|  3. Call retriever.search -------+--> retriever.py --> embeddings.py --> Pinecone
|  4. Call generate_itinerary -----+--> itinerary_generator.py --> Groq LLM
|  5. Build ItineraryResponse -----+--> models.py
|  6. Return JSON to client        |
+----------------------------------+
```

`main.py` imports and calls every module we built. It is the orchestrator. It does not contain any business logic itself. Its only job: receive the request, call the right modules in the right order, handle errors, and return the result.

### What each new piece does

- **API key authentication** — checks every incoming request for an `X-API-Key` header. If the key doesn't match `.env`, the request is rejected with 401 Unauthorized.
- **The `/api/v1/plan-trip` endpoint** — receives `ChatRequest`, runs the three-step pipeline (extract -> search -> generate), returns `ItineraryResponse`.
- **Error handling** — `try/except` blocks around every external API call. If Groq is down, returns 502. If Pinecone is down, returns 503.
- **Rate limiting** — limits each client to 50 requests per minute. Prevents one client from burning through free-tier API quota.
- **LRU cache** — if two clients send the exact same messages, skip the pipeline and return the cached result.
- **Processing time tracking** — measures pipeline duration in milliseconds.

---

## 4. File Update 1: config.py — Added APP_API_KEY

### The line added

```python
# --- API Authentication ---
APP_API_KEY: str = os.getenv("APP_API_KEY", "")
```

### Line-by-line explanation

**LINE:** `APP_API_KEY: str = os.getenv("APP_API_KEY", "")`

WHAT it does
- Reads a value called `APP_API_KEY` from the `.env` file (through environment variables) and stores it in a Python variable. If no value is found, defaults to an empty string.

WHY it exists
- `main.py` checks every incoming request for an API key. It needs to know what the correct key is. This line loads the correct key from the environment so `main.py` can compare against what the client sends.

HOW it connects
- `main.py` imports `APP_API_KEY` from `config.py`, same pattern as `intent_extractor.py` importing `GROQ_API_KEY`.

### Full updated config.py

```python
"""Centralized configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq, free tier) ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")

# --- Pinecone ---
PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "travel-rag")

# --- Embeddings ---
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- Server ---
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# --- API Authentication ---
APP_API_KEY: str = os.getenv("APP_API_KEY", "")
```

---

## 5. File Update 2: .env and .env.example — Added APP_API_KEY

### .env (real secrets — git-ignored)

Added at the end:
```
# === API Authentication ===
APP_API_KEY=dev-travel-key-2026
```

### .env.example (template for developers — committed to Git)

Added at the end:
```
# === API Authentication ===
APP_API_KEY=your_api_key_here
```

### Why two files

`.env` holds real secrets. It is in `.gitignore`, never pushed to GitHub. `.env.example` is a template — shows other developers what variables they need to set, with fake placeholder values. Committed to Git so other developers know what to configure.

---

## 6. File Update 3: models.py — Added summary Field

### The line added

Inside `ItineraryResponse`:
```python
summary: str = Field("", description="LLM-generated friendly travel recommendation")
```

### Line-by-line explanation

**LINE:** `summary: str = Field("", description="LLM-generated friendly travel recommendation")`

WHAT it does
- Adds a new field called `summary` to the response model. Type is `str`. Default is empty string `""`.

WHY it exists
- `itinerary_generator.generate_itinerary()` returns a plain-text travel summary. Before this change, `ItineraryResponse` had no place for that text. Without this field, the summary would be lost — the client would get hotels and flights but never see the friendly recommendation.

WHY `""` as default instead of `Optional[str] = None`
- `itinerary_generator.py` always returns a string — either the LLM output or a fallback message like "Itinerary summary unavailable...". It never returns `None`. Default `""` matches the actual behavior.

### Full updated models.py

```python
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
    messages: list[dict] = Field(..., description="List of {user, text} message dicts")
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
```

---

## 7. File Built: app/main.py — Full Code

```python
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
    description="Agentic travel planning pipeline: intent extraction -> RAG search -> itinerary generation",
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
# Result builders -- convert raw Pinecone matches to Pydantic models
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
    Full pipeline: extract intent -> search Pinecone -> generate itinerary.
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
```

---

## 8. Line-by-Line Teach-Through: main.py

### Section 1: Imports (lines 9-26)

**`import time`**
- Python's built-in module for measuring time. We use `time.time()` to capture the moment before and after the pipeline runs, then subtract to get processing duration in milliseconds.
- If removed: cannot measure how long a request takes.

**`import hashlib`**
- Python's built-in module for creating hash values. A hash takes any input (like a block of text) and produces a fixed-length string that uniquely represents that input. We use it to create a cache key — a short fingerprint of incoming chat messages.
- If removed: cannot cache repeated requests.

**`import json`**
- Python's built-in module for converting Python objects to JSON strings and back. `hashlib` requires a string as input. The incoming messages are a list of dictionaries. `json.dumps()` converts that list into a string so we can hash it.
- If removed: cannot convert the messages list into a hashable string.

**`from fastapi import FastAPI, HTTPException, Security`**
- `FastAPI` — the class that creates the web application object. This object receives HTTP requests and sends responses. Without it, no web server.
- `HTTPException` — a special error class. When raised, FastAPI automatically sends back an HTTP error response with a status code (like 401 or 503) and an error message. Without it, errors crash the server instead of returning clean error responses.
- `Security` — a FastAPI function that plugs into the request pipeline. Tells FastAPI: "before running my endpoint code, first run this security check." Without it, no way to enforce API key authentication.

**`from fastapi.security import APIKeyHeader`**
- A class that tells FastAPI to look for a specific HTTP header in every request. We configure it to look for `X-API-Key`. When a request arrives, FastAPI pulls the value from that header and passes it to our verification function.
- If removed: FastAPI doesn't know where to find the API key.

**`from app.config import APP_API_KEY, HOST, PORT`**
- `APP_API_KEY` — the correct API key to compare against (from `.env`).
- `HOST` — what network address to listen on (default `"0.0.0.0"` = all addresses).
- `PORT` — what port number to listen on (default `8000`).
- If removed: don't know the correct API key, don't know what address to listen on.

**`from app.models import ChatRequest, ItineraryResponse, ItineraryHotel, ItineraryFlight, TravelIntent`**
- All Pydantic models. `ChatRequest` = incoming request shape. `ItineraryResponse` = outgoing response shape. `ItineraryHotel`, `ItineraryFlight` = used to build individual result items. `TravelIntent` = imported but used implicitly through the pipeline.
- If removed: no data validation, no response structure.

**`from app.intent_extractor import extract_intent`**
- The function that takes raw chat messages and returns a structured `TravelIntent`. Step 1 of the pipeline.
- If removed: cannot extract travel preferences from chat.

**`from app.retriever import search`**
- The function that takes a `TravelIntent` and searches Pinecone for matching hotels and flights. Step 2 of the pipeline.
- If removed: cannot find matching results.

**`from app.itinerary_generator import generate_itinerary`**
- The function that takes intent + search results and generates a friendly text summary. Step 3 of the pipeline.
- If removed: response has no summary.

### Section 2: App initialization (lines 32-36)

**`app = FastAPI(title="Travel RAG API", version="1.0.0", description="...")`**

WHAT it does
- Creates the FastAPI application object. The actual web server. Every endpoint defined later attaches to this object. The `title`, `version`, and `description` are metadata that appear on the auto-generated Swagger docs page at `/docs`.

WHY it exists
- Without it, no server. No `app` object means no endpoints, no request handling, nothing listens on any port.

WHAT happens under the hood
```
Step 1 -> Python calls the FastAPI() constructor
Step 2 -> FastAPI creates an internal routing table (empty — no endpoints yet)
Step 3 -> The metadata is stored for the docs page
Step 4 -> The app object is ready to receive endpoint definitions
```

HOW it connects
- Every `@app.post(...)` decorator later in the file attaches to this object.
- `uvicorn` needs this object to know what to serve.

### Section 3: API key authentication (lines 38-47)

**`api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)`**

WHAT it does
- Creates a security scheme telling FastAPI: "look for a header called `X-API-Key` in every incoming request." `auto_error=False` means: if the header is missing, don't auto-throw an error — pass `None` to our verification function so we handle it ourselves.

WHY it exists
- Without it, FastAPI doesn't know where to find the API key.

HOW it connects
- `verify_api_key` uses this via `Security(api_key_header)`.

**`def verify_api_key(key: str = Security(api_key_header)) -> str:`**

WHAT it does
- A function that receives the API key from the header and checks if it's correct. `Security(api_key_header)` tells FastAPI: "before calling this function, extract the `X-API-Key` header and pass its value as `key`."

**`if not APP_API_KEY: return "no-auth"`**

WHAT it does
- If the server owner hasn't set `APP_API_KEY` in `.env`, skip authentication entirely. For local development — you don't need API keys while testing on your own machine.

WHY it exists (critical — taught through Q&A)
- Without this guard, if `APP_API_KEY` is `""` (empty string), EVERY request gets rejected. `key != ""` is always `True` for any non-empty key the client sends. The developer gets 401 errors even though they did nothing wrong — they just forgot to set a variable in `.env`.
- The guard says: "If the server owner hasn't configured auth, let everyone through."

**`if key != APP_API_KEY: raise HTTPException(status_code=401, detail="Invalid or missing API key")`**

WHAT it does
- Compares what the client sent against the real key from `.env`. If they don't match, raises 401 Unauthorized.

HOW the whole function connects
```
depends on -> APP_API_KEY from config.py (the correct key)
depends on -> api_key_header (extracts the key from the request)
affects   -> every endpoint that uses Security(verify_api_key) — blocks the request if the key is wrong
```

### Section 4: Rate limiting (lines 53-69)

**`_request_log: dict[str, list[float]] = {}`**

WHAT it does
- An empty dictionary in the server's memory for the entire time the server runs. Keys are API key strings (one per client). Values are lists of timestamps — each is a floating-point number representing when a request was made.

WHAT it looks like in practice
```python
{
    "dev-travel-key-2026": [1711900000.1, 1711900001.5, 1711900003.2],
    "another-key-xyz":     [1711900002.8]
}
```

**`RATE_LIMIT = 50`** and **`RATE_WINDOW = 60`**
- Two constants. Maximum 50 requests within a 60-second window per client.

**`def _check_rate_limit(api_key: str) -> None:`**
- Enforces the rate limit. Takes the client's API key to track each client separately.

**`now = time.time()`**
- Captures the current moment as a Unix timestamp (seconds since January 1, 1970). Example: `1711900005.347`.

**`timestamps = _request_log.get(api_key, [])`**
- Looks up this client's history. If the client has made requests before, gets their timestamps. First request ever returns `[]`.

**`timestamps = [t for t in timestamps if now - t < RATE_WINDOW]`** (CRITICAL LINE)

WHAT it does
- Filters the list. Keeps only timestamps from the last 60 seconds. Throws away anything older.

WHAT happens under the hood
```
Step 1 -> Loop through every timestamp in the list
Step 2 -> For each, calculate: current time minus that timestamp
Step 3 -> If result < 60 -> keep it (recent)
Step 4 -> If result >= 60 -> discard it (too old)
```

WHY it exists (taught through Q&A — two problems it prevents)
1. **False rejections** — without filtering, timestamps accumulate forever. After 51 total requests (even spread over hours), `len(timestamps) > 50` becomes True. Legitimate users get permanently blocked.
2. **Memory leak** — without cleanup, the list grows infinitely. After days of running, thousands of timestamps eat memory until the server slows down or crashes.

**`timestamps.append(now)`**
- Adds the current request's timestamp.

**`_request_log[api_key] = timestamps`**
- Saves the updated list back into the dictionary.

**`if len(timestamps) > RATE_LIMIT: raise HTTPException(status_code=429, ...)`**
- If more than 50 timestamps in the filtered list, this client exceeded the limit. 429 = "Too Many Requests."

### Section 5: Caching helper (lines 75-82)

**`def _make_cache_key(messages: list[dict]) -> str:`**
- Takes the incoming messages and returns a unique string fingerprint.

**`raw = json.dumps(messages, sort_keys=True)`**

WHAT it does
- Converts the list of dictionaries into a single JSON string. `sort_keys=True` sorts dictionary keys alphabetically before converting.

WHY `sort_keys=True` matters (taught through Q&A)
- Without it, `{"user": "Alice", "text": "hi"}` and `{"text": "hi", "user": "Alice"}` produce different strings, which produce different hashes. The same request would be treated as new. `sort_keys=True` forces both into the same order, so they produce the same hash. No duplicate cache entries.

**`return hashlib.sha256(raw.encode()).hexdigest()`**

Three operations chained:
```
Step 1 -> raw.encode()      — converts string to bytes (hashlib requires bytes)
Step 2 -> hashlib.sha256()  — feeds bytes into SHA-256 hash algorithm
                               produces a fixed-length fingerprint (64 chars)
Step 3 -> .hexdigest()      — converts fingerprint to readable hex string
                               example: "a3f8b2c1d4e5..."
```

**`_result_cache: dict[str, dict] = {}`** and **`MAX_CACHE_SIZE = 128`**
- `_result_cache` stores previous results. Key = hash string. Value = full pipeline result.
- `MAX_CACHE_SIZE` = at most 128 entries. If reached, clear cache to prevent memory growth.

### Full cache flow (taught through Q&A)

```
Client A sends: [{"user": "Alice", "text": "beach trip"}]

Step 1 -> json.dumps() converts list to string: '[{"text": "beach trip", "user": "Alice"}]'
Step 2 -> hashlib takes string -> hash: "a3f8b2c1..."
Step 3 -> lru_cache checks: "Have I seen this hash?" -> NO (first time)
       -> Runs full pipeline (extract -> search -> generate)
       -> Stores: hash -> full result
Step 4 -> Returns result to Client A
```

```
Client B sends: [{"user": "Alice", "text": "beach trip"}]  (same messages)

Step 1 -> json.dumps() -> same string
Step 2 -> hashlib -> same hash: "a3f8b2c1..."
Step 3 -> Cache checks: "Have I seen this hash?" -> YES
       -> SKIPS entire pipeline
       -> Returns stored result from memory
Step 4 -> Client B gets same result instantly
          No Groq call. No Pinecone call. No waiting.
```

**What `_result_cache` stores: the hash paired with the full result. When it sees the same hash again, it returns the stored result and skips the entire function.**

### Section 6: Result builders (lines 88-121)

**`_build_hotel(match: dict) -> ItineraryHotel`** and **`_build_flight(match: dict) -> ItineraryFlight`**

WHAT they do
- Pinecone returns raw dictionaries with a flat `metadata` field. Our API response uses structured Pydantic models. These functions convert from one format to the other.

WHY they exist
- Without them, all conversion logic sits inside the endpoint function, making it long and messy.

The defensive pattern — `.get("key", default)`
- Every metadata field uses `.get()` with a default instead of direct access `m["name"]`. If Pinecone returns a record missing a field, `.get()` returns the default. `m["name"]` would throw `KeyError` and crash the entire request.

The `amenities` special case
- In `retriever.py`, amenities were stored as comma-separated string: `"pool,spa,gym"`. Now we convert back to list: `["pool", "spa", "gym"]`. That's what `amenities_raw.split(",")` does.

### Section 7: The endpoint (lines 127-190) — THE HEART OF main.py

**`@app.post("/api/v1/plan-trip", response_model=ItineraryResponse)`**

WHAT it does
- Decorator attaching the function to the `app` object: "When an HTTP POST arrives at `/api/v1/plan-trip`, run this function." `response_model=ItineraryResponse` tells FastAPI to validate the output and generate docs from it.

**`def plan_trip(request: ChatRequest, api_key: str = Security(verify_api_key)):`**

WHAT it does
- Two parameters:
  - `request: ChatRequest` — FastAPI auto-parses incoming JSON body into a `ChatRequest` Pydantic object. If JSON doesn't match schema, FastAPI returns 422 before this function runs.
  - `api_key: str = Security(verify_api_key)` — FastAPI calls `verify_api_key()` first. If key is wrong, function never executes.

**`_check_rate_limit(api_key)`**
- Calls the rate limiter. If this client exceeded 50 req/60s, raises 429.

**Cache check block:**
```python
cache_key = _make_cache_key(request.messages)
if cache_key in _result_cache:
    return ItineraryResponse(**_result_cache[cache_key])
```
- Generates hash fingerprint. Checks if seen before. If yes, returns stored result immediately — skips entire pipeline.

**`start = time.time()`**
- Records time before pipeline runs.

**Step 1 — Extract intent:**
```python
try:
    intent = extract_intent(request.messages)
except Exception as e:
    raise HTTPException(status_code=502, detail=f"Intent extraction failed: {e}")
```
- Calls intent extractor (Phase 1). If Groq is down or LLM returns garbage, returns **502 Bad Gateway** — "our upstream service failed."

**Step 2 — Search Pinecone:**
```python
try:
    results = search(intent, top_k=request.top_k)
except Exception as e:
    raise HTTPException(status_code=503, detail=f"Search service unavailable: {e}")
```
- Calls retriever (Phase 2). If Pinecone is down, returns **503 Service Unavailable**.

**Step 3 — Generate itinerary (DIFFERENT error handling — taught through Q&A):**
```python
try:
    summary = generate_itinerary(intent, results)
except Exception:
    summary = "Itinerary summary could not be generated at this time."
```
- Instead of raising an error, sets a fallback message. The request STILL SUCCEEDS.

WHY Step 3 handles errors differently from Steps 1 and 2:
- **Steps 1 and 2 are essential.** No intent = no search. No search = no results. Without them, the response is meaningless. Must fail with an error.
- **Step 3 is nice-to-have.** The hotels and flights ARE the real value. If the LLM fails, we still return useful data. The client can see all results and make their own decisions. Crashing the whole request just because the summary text failed would throw away all that useful data.

**Build response block:**
```python
hotels = [_build_hotel(h) for h in results.get("hotels", [])]
flights = [_build_flight(f) for f in results.get("flights", [])]
elapsed_ms = round((time.time() - start) * 1000, 2)
```
- Converts raw Pinecone matches to Pydantic objects via helper functions.
- Calculates processing time: `time.time() - start` gives seconds. Multiply by 1000 for ms. `round(..., 2)` keeps 2 decimal places.

**Cache storage block:**
```python
if len(_result_cache) >= MAX_CACHE_SIZE:
    _result_cache.clear()
_result_cache[cache_key] = response_data
```
- If cache has 128+ entries, clear entirely to prevent unbounded memory growth. Then store this result.

**`return ItineraryResponse(**response_data)`**
- `**response_data` unpacks the dictionary into keyword arguments. FastAPI takes the Pydantic object, converts to JSON, sends as HTTP response.

### Section 8: Server runner (lines 196-198)

**`if __name__ == "__main__":`**
- Checks: "Is this file being run directly?" If yes, execute code below. If imported by another file, skip. Prevents server from starting accidentally on import.

**`uvicorn.run(app, host=HOST, port=PORT)`**
- Starts the actual web server. `uvicorn` is an ASGI server — listens on a network port and forwards HTTP requests to our `app` object. `HOST="0.0.0.0"` = accept from any IP. `PORT=8000` = listen on port 8000.

---

## 9. Q&A and Teaching Discussions

### Q&A 1: What do hashlib, json, and lru_cache do for caching?

**Question asked:** "We import hashlib and json for caching. Walk me through exactly what happens when two different clients send the exact same list of chat messages."

**Sean's initial answer (paraphrased):** "It gets caught in the lru cache. json is the one that creates the string for the hash. hashlib converts the text messages into unique [fingerprints]."

**Follow-up question asked:** "Walk through what happens to Client B's request at each step."

**Sean's answer:** "json converts them to string and hashlib converts that string to hashcode and the lru cache keeps the record of that string conversion to hash as the second user asks the same thing again."

**Follow-up question:** "Which thing does lru_cache actually store — the hash, or the function's full result?"

**Sean's answer:** "A — sees the hash, finds the matching hash, returns the stored pipeline result without running the pipeline again."

**Final understanding confirmed:** "lru_cache contains the hash and the full result so it does not run the full function again — instead it just gets the stored value."

**Verdict:** Correct. The cache stores the pairing: hash -> full result. When it sees the same hash, it returns the stored result and skips everything.

### Q&A 2: sort_keys=True — why both dictionaries produce different hashes

**Question asked:** "Give me two dictionaries that are logically identical but would produce different cache keys without sort_keys=True."

**Sean's answer:** `{"user": "Alice", "text": "hi"}` and `{"text": "hi", "user": "Alice"}` — "SHA algorithm makes new string for unique output, it will make two input hash keys uniquely for these two as well without sort_keys=True. So it helps in preventing duplication."

**Verdict:** Correct. Same data, different key order, different strings, different hashes, duplicate cache entries. `sort_keys=True` forces alphabetical order before conversion, producing identical strings.

### Q&A 3: The `if not APP_API_KEY` guard line

**Question asked:** "What would happen if we removed the `if not APP_API_KEY: return 'no-auth'` line and a developer runs the server locally without setting APP_API_KEY?"

**Sean's initial answer (paraphrased):** "It will check in the next if condition and show invalid API key."

**Follow-up teaching:** Explained that `APP_API_KEY = ""` (empty string) and `key = "some-key-123"`, so `key != APP_API_KEY` evaluates to `"some-key-123" != ""` which is `True`. Every request gets rejected even though the developer did nothing wrong.

**Sean's corrected understanding:** "This is for local development help. In case the developer forgot to add the key in the .env file, the authorization still works and the flow goes through without any hindrance."

**Verdict:** Correct. The guard skips authentication entirely when `APP_API_KEY` is not configured, so local development works without needing to set up auth.

### Q&A 4: Rate limiter filtering line

**Question asked:** "Why do we need the `timestamps = [t for t in timestamps if now - t < RATE_WINDOW]` filtering step? What would go wrong without it?"

**Sean's answer:** "This filtering is required in order to keep only those timestamps which are made in the last 60 second window."

**Follow-up question:** "What would go wrong if we removed it and just kept appending forever?"

**Sean's answer after guidance:** "Preventing the legitimate user from getting 429 error because it is a timestamp thing, so that even if timestamps before 60 seconds have more than 50 requests it doesn't get blocked. And memory leak — making the system crash on appending so many requests."

**Verdict:** Correct. Two problems: (1) false rejections — legitimate users permanently blocked after 51 total requests ever, (2) memory leak — list grows forever, server crashes.

### Q&A 5: Why Step 3 uses fallback instead of raising error

**Question asked:** "Step 3 (itinerary generator) handles errors differently from Steps 1 and 2. Why?"

**Sean's initial answer:** "Because at least we want to get the results despite the exception."

**Follow-up question:** "Which results specifically?"

**Sean's answer after guidance:** "The hotels and flights list on the basis of the intent."

**Final understanding:** "Step 3 uses a fallback because the summary only has sense if it has the intent. There is no use making the error handling complex when the input is not there for that function."

**Corrected framing:** Step 3 uses a fallback because the hotels and flights are the real value. If the summary fails, the client still receives all the useful search results. Crashing the entire request just because the friendly text failed would throw away useful data.

---

## 10. Connection Summary — main.py

```
CONNECTION SUMMARY -- main.py

This file receives:
+-- APP_API_KEY, HOST, PORT from config.py -- used for auth and server startup
+-- ChatRequest, ItineraryResponse, ItineraryHotel, ItineraryFlight from models.py -- used for validation
+-- extract_intent from intent_extractor.py -- Step 1 of pipeline
+-- search from retriever.py -- Step 2 of pipeline
+-- generate_itinerary from itinerary_generator.py -- Step 3 of pipeline

This file sends:
+-- JSON response to the HTTP client -- the only outward-facing output

If this file were deleted:
+-- Every other file still works as standalone Python
+-- But no client can reach the pipeline over the network
+-- The entire system becomes unusable from outside

If any other file were deleted:
+-- config.py deleted -> main.py crashes on import (no APP_API_KEY, HOST, PORT)
+-- models.py deleted -> main.py crashes on import (no ChatRequest, ItineraryResponse)
+-- intent_extractor.py deleted -> main.py crashes on import (no extract_intent)
+-- retriever.py deleted -> main.py crashes on import (no search)
+-- itinerary_generator.py deleted -> main.py crashes on import (no generate_itinerary)
```

---

## 11. Full End-to-End Request Flow

```
[Client sends POST /api/v1/plan-trip with JSON body and X-API-Key header]
     |
     v
Step 1: FastAPI extracts X-API-Key header value
     |
     v
Step 2: verify_api_key() checks key against APP_API_KEY from .env
     |  (if invalid -> 401 Unauthorized)
     |  (if APP_API_KEY not set -> skip auth, return "no-auth")
     v
Step 3: _check_rate_limit() checks if client exceeded 50 req/60s
     |  (if exceeded -> 429 Too Many Requests)
     v
Step 4: _make_cache_key() hashes the messages with SHA-256
     |
     v
Step 5: Cache check -- if hash exists in _result_cache -> return stored result immediately
     |  (if cache hit -> skip everything below, return instantly)
     v
Step 6: time.time() captures start timestamp
     |
     v
Step 7: extract_intent(messages) -> TravelIntent
     |  (calls intent_extractor.py -> which calls Groq LLM or rule-based fallback)
     |  (if fails -> 502 Bad Gateway)
     v
Step 8: search(intent, top_k) -> {hotels: [...], flights: [...]}
     |  (calls retriever.py -> which calls embeddings.py -> which calls Pinecone)
     |  (if fails -> 503 Service Unavailable)
     v
Step 9: generate_itinerary(intent, results) -> summary text
     |  (calls itinerary_generator.py -> which calls Groq LLM)
     |  (if fails -> fallback message, request still succeeds)
     v
Step 10: _build_hotel() / _build_flight() convert raw dicts to Pydantic models
     |
     v
Step 11: Calculate elapsed_ms = (time.time() - start) * 1000
     |
     v
Step 12: Store result in _result_cache (clear if cache >= 128 entries)
     |
     v
Step 13: Return ItineraryResponse as JSON to client
```

---

## 12. Cumulative Connection Map (Phase 1 + 2 + 3)

```
config.py ---------> intent_extractor.py (GROQ_API_KEY, LLM_MODEL)
    |
    +-------------> embeddings.py (EMBEDDING_MODEL)
    |
    +-------------> retriever.py (PINECONE_API_KEY, PINECONE_INDEX_NAME)
    |
    +-------------> itinerary_generator.py (GROQ_API_KEY, LLM_MODEL)
    |
    +-------------> main.py (APP_API_KEY, HOST, PORT)              <-- NEW

models.py --------> intent_extractor.py (TravelIntent)
    |
    +-------------> embeddings.py (TravelIntent via intent_to_query)
    |
    +-------------> retriever.py (TravelIntent)
    |
    +-------------> itinerary_generator.py (TravelIntent)
    |
    +-------------> main.py (ChatRequest, ItineraryResponse,       <-- NEW
    |                        ItineraryHotel, ItineraryFlight)

embeddings.py ----> retriever.py (embed_text, embed_texts, record_to_text, intent_to_query)

intent_extractor.py ----> main.py (extract_intent)                 <-- NEW
retriever.py -----------> main.py (search)                         <-- NEW
itinerary_generator.py -> main.py (generate_itinerary)             <-- NEW

main.py (ORCHESTRATOR) calls in order:
    1. intent_extractor.extract_intent()
    2. retriever.search()
    3. itinerary_generator.generate_itinerary()
    -> Returns ItineraryResponse to HTTP client

scripts/ingest_to_pinecone.py --> retriever.py (calls ingest_records)
```

---

## 13. Final Project File Tree

```
project/
+-- .env                              # Real secrets (git-ignored)
+-- .env.example                      # Template for developers
+-- .gitignore                        # Prevents .env, __pycache__ from Git
+-- CLAUDE.md                         # Senior mentorship protocol
+-- PHASE_1_REFERENCE.md              # Phase 1 complete reference
+-- PHASE_2_REFERENCE.md              # Phase 2 complete reference
+-- SESSION_3_CHAT_REFERENCE.md       # Session 3 chat reference (itinerary_generator)
+-- SESSION_4_CHAT_REFERENCE.md       # THIS FILE — Session 4 chat reference (main.py)
+-- requirements.txt                  # Python dependencies
+-- app/
|   +-- __init__.py                   # Package marker (empty)
|   +-- config.py                     # Environment variable loader (24 lines) -- UPDATED
|   +-- models.py                     # Pydantic data models (72 lines) -- UPDATED
|   +-- intent_extractor.py           # Chat -> TravelIntent (148 lines)
|   +-- embeddings.py                 # Text -> vectors (72 lines)
|   +-- retriever.py                  # Pinecone ingest + search (197 lines)
|   +-- itinerary_generator.py        # Intent + results -> summary (148 lines)
|   +-- main.py                       # FastAPI server (199 lines) -- NEW
+-- scripts/
|   +-- generate_mock_data.py         # Generate 11,000 mock records
|   +-- ingest_to_pinecone.py         # Load records into Pinecone
+-- data/
|   +-- sample_chats.json             # 5 example group chats
|   +-- hotels.json                   # 5,500 hotel records
|   +-- flights.json                  # 5,500 flight records
|   +-- all_records.json              # Combined hotels + flights
+-- tests/
    (empty)
```

---

## 14. All Code Files — Final State

### app/config.py (24 lines)

```python
"""Centralized configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq, free tier) ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-70b-versatile")

# --- Pinecone ---
PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "travel-rag")

# --- Embeddings ---
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# --- Server ---
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# --- API Authentication ---
APP_API_KEY: str = os.getenv("APP_API_KEY", "")
```

### app/models.py (72 lines)

```python
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
    messages: list[dict] = Field(..., description="List of {user, text} message dicts")
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
```

### app/intent_extractor.py (148 lines)

```python
"""
Agentic LangChain pipeline to extract structured travel intent
from unstructured group chat messages.

Uses Groq (Llama 3.1 70B) -- free tier, fast inference.
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
    return "\n".join(f"{m['user']}: {m['text']}" for m in messages)


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
    r"|(?:\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:\s*[-\u2013to]+\s*\d{1,2})?\b)"
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
    """Regex + heuristic extraction -- works offline with no API key."""
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
```

### app/embeddings.py (72 lines)

```python
"""
Embedding utilities — converts text into 384-dimensional vectors
using a local sentence-transformers model (free, offline).
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL
from app.models import TravelIntent


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model once and cache it in memory."""
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """Embed a single text string into a 384-dimensional vector."""
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a single batch (faster than one-at-a-time)."""
    model = get_model()
    vectors = model.encode(texts, normalize_embeddings=True, batch_size=256)
    return vectors.tolist()


def record_to_text(record: dict) -> str:
    """
    Convert a hotel or flight record dict into a natural-language sentence
    suitable for embedding. The embedding model understands sentences better
    than raw JSON.
    """
    if record["type"] == "hotel":
        amenities_str = ", ".join(record.get("amenities", []))
        return (
            f"{record['name']} -- a {record['stars']}-star {record['vibe']} hotel "
            f"in {record['destination']}. ${record['price_per_night']:.2f}/night. "
            f"Rating: {record['rating']}/5. Amenities: {amenities_str}."
        )
    elif record["type"] == "flight":
        stops = "nonstop" if record.get("stops", 0) == 0 else f"{record['stops']} stop(s)"
        return (
            f"{record['airline']} flight from {record.get('origin', 'Unknown')} to "
            f"{record['destination']}. {record['cabin_class'].replace('_', ' ').title()} class. "
            f"${record['price']:.2f}. Departs {record.get('departure_date', 'TBD')}. "
            f"{record.get('duration_hours', 0):.1f} hours, {stops}. Rating: {record['rating']}/5."
        )
    return str(record)


def intent_to_query(intent: TravelIntent) -> str:
    """Convert a TravelIntent into a natural-language search query."""
    parts = []
    if intent.vibe:
        parts.append(f"{intent.vibe} destination")
    if intent.destination:
        parts.append(f"in or near {intent.destination}")
    if intent.budget_per_person is not None:
        parts.append(f"under ${intent.budget_per_person} per person")
    if intent.check_in:
        parts.append(f"from {intent.check_in}")
    if intent.check_out:
        parts.append(f"to {intent.check_out}")
    if intent.amenities:
        parts.append(f"with {', '.join(intent.amenities)}")
    return " ".join(parts) if parts else "travel destination"
```

### app/retriever.py (197 lines)

```python
"""
Pinecone-backed retriever for the travel RAG pipeline.

Two responsibilities:
1. Ingestion -- embed all hotel/flight records and upsert into Pinecone
2. Search   -- embed a TravelIntent query and retrieve top-k matches
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
# Ingestion -- load records into Pinecone
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
# Search -- retrieve matching hotels and flights
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
```

### app/itinerary_generator.py (148 lines)

```python
"""
Itinerary generator -- passes extracted intent and RAG search results
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
# Helper -- format search results into readable text
# ---------------------------------------------------------------------------
def _format_hotel(match: dict, rank: int) -> str:
    """Convert a single Pinecone hotel match into a readable line."""
    meta = match["metadata"]
    return (
        f"{rank}. {meta.get('name', 'Unknown')} -- "
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
        f"{rank}. {meta.get('airline', 'Unknown')} -- "
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
```

### app/main.py (199 lines)

(Full code already shown in Section 7 above)

---

## 15. Key Concepts Learned This Session

- **FastAPI app object** — `FastAPI()` creates the web server. Endpoints attach to it via decorators like `@app.post(...)`. `uvicorn` runs it.
- **APIKeyHeader + Security** — FastAPI's built-in way to extract and validate API keys from HTTP headers. `APIKeyHeader` defines which header to look for. `Security()` tells FastAPI to run verification before the endpoint.
- **The `if not APP_API_KEY` guard** — skips authentication when no key is configured in `.env`. Prevents false 401 rejections during local development.
- **In-memory rate limiting** — dictionary of `{api_key: [timestamps]}`. Filter old timestamps (>60s), append current, check count. Prevents API quota abuse. Two problems without filtering: false rejections of legitimate users, and memory leak.
- **SHA-256 cache keys** — `json.dumps(messages, sort_keys=True)` produces deterministic string. `hashlib.sha256()` produces unique fingerprint. Cache stores hash -> full result. Same messages -> same hash -> skip pipeline.
- **`sort_keys=True`** — forces dictionary keys into alphabetical order before converting to string. Prevents logically identical dictionaries from producing different hashes.
- **Manual dictionary cache with MAX_CACHE_SIZE** — `_result_cache` stores up to 128 results. Cleared entirely when full to prevent unbounded memory growth.
- **Differentiated error handling** — essential steps (intent extraction, search) raise HTTP errors on failure (502, 503). Nice-to-have steps (summary generation) use fallback values so the request still succeeds with useful data.
- **HTTP status codes used:** 200 (success), 401 (unauthorized), 422 (validation error — automatic from Pydantic), 429 (rate limit exceeded), 502 (upstream service failed — Groq), 503 (service unavailable — Pinecone)
- **`response_model=ItineraryResponse`** — tells FastAPI to validate output against the Pydantic model and use it for auto-generated docs.
- **`Security(verify_api_key)` as default parameter** — FastAPI runs verify_api_key before the endpoint function. If verification fails, endpoint never executes.
- **Result builder pattern** — `_build_hotel()` / `_build_flight()` convert raw Pinecone dictionaries to structured Pydantic models. Keeps the endpoint function clean.
- **Defensive `.get()` with defaults** — every metadata field uses `.get("key", default)` to prevent `KeyError` from one bad record crashing the entire request.
- **`amenities_raw.split(",")` pattern** — converting comma-separated string back to list. Needed because Pinecone stores amenities as a string (ingestion) but we want a list (response).
- **`**response_data` unpacking** — converts a dictionary into keyword arguments for the Pydantic model constructor.
- **`if __name__ == "__main__"`** — prevents server from starting when file is imported. Only starts when run directly.
- **`uvicorn`** — ASGI server that listens on a network port and forwards HTTP requests to the FastAPI app. `host="0.0.0.0"` = accept from any IP.

---

## 16. Interview Prep Checkpoints

### Interview Question 1: API Authentication

**Q:** "How do you protect your API from unauthorized access?"

**A:** "I use API key authentication via FastAPI's built-in Security system. Every request must include an X-API-Key header. The server compares it against a key stored in an environment variable. If it doesn't match, the server returns a 401 Unauthorized. I also added a guard so that if no API key is configured in the environment, authentication is skipped entirely — this makes local development painless without compromising production security."

### Interview Question 2: Rate Limiting

**Q:** "How do you handle rate limiting in your API?"

**A:** "I built an in-memory rate limiter using a sliding window approach. Each client's API key maps to a list of request timestamps. On every request, I filter out timestamps older than 60 seconds, add the current one, and check if the count exceeds 50. If it does, I return a 429 Too Many Requests. The filtering step is critical — without it, timestamps accumulate forever, causing false rejections of legitimate users and memory leaks."

### Interview Question 3: Caching Strategy

**Q:** "How do you handle caching for repeated requests?"

**A:** "I hash the incoming chat messages using SHA-256 to create a unique cache key. If the same messages come in again, the hash matches and I return the cached result immediately — no LLM call, no Pinecone query. I use sort_keys=True in json.dumps so that dictionaries with the same data but different key orders produce the same hash. The cache is capped at 128 entries to prevent unbounded memory growth."

### Interview Question 4: Error Handling Strategy

**Q:** "How do you handle failures in your pipeline?"

**A:** "I use differentiated error handling. Intent extraction and vector search are essential — if they fail, I return HTTP errors (502 for Groq failures, 503 for Pinecone). But the itinerary summary is nice-to-have. If the LLM fails to generate it, I set a fallback message and still return all the hotel and flight results. The client gets useful data even when one component is down."

### Interview Question 5: Full Pipeline

**Q:** "Walk me through what happens when a request hits your API."

**A:** "The request goes through several layers: first API key verification, then rate limiting, then a cache check. If it's a cache miss, the pipeline runs three steps — intent extraction from the chat messages using Groq, vector search in Pinecone for matching hotels and flights, and summary generation via LLM. Raw Pinecone results get converted to structured Pydantic models, the response is cached for future identical requests, and JSON is returned to the client with processing time included."

---

## 17. What Remains After This Session

| Task | Status |
|---|---|
| `app/main.py` — FastAPI server | BUILT |
| `config.py` update — APP_API_KEY | DONE |
| `models.py` update — summary field | DONE |
| `.env` / `.env.example` update | DONE |
| `itinerary_generator.py` (from Session 3) | BUILT |
| Comprehension check (explain back) | PENDING |
| PHASE_3_REFERENCE.md | PENDING |
| Swagger UI verification | PENDING |
| GitHub push checkpoint | PENDING |
| Docker containerization (Phase 4 if planned) | NOT STARTED |

---

*This reference captures the complete Session 4 chat — every file change, every line-by-line explanation, every Q&A exchange, every teaching moment. Use it alongside SESSION_3_CHAT_REFERENCE.md, PHASE_1_REFERENCE.md, and PHASE_2_REFERENCE.md for the full project history.*
