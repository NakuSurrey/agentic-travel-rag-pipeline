# Agentic Travel Intent & RAG Pipeline

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-orange?logo=chainlink&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-purple)
![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?logo=docker&logoColor=white)
![Deployed](https://img.shields.io/badge/Hetzner-Live-green?logo=hetzner&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade REST API that reads unstructured group chat messages, extracts travel intent using an LLM, searches a vector database for matching hotels and flights, and generates a friendly itinerary summary — all in one request.

## Live Demo

> **Visual Demo:** [`http://46.225.208.197/travel-demo/`](http://46.225.208.197/travel-demo/) — type a group chat, see the full pipeline in action
>
> **API Docs:** [`http://46.225.208.197/travel-api/docs`](http://46.225.208.197/travel-api/docs) — interactive Swagger UI
>
> API requires `X-API-Key` header for authentication.

## What It Does

- **Extracts travel intent from messy group chats** — destination, vibe, budget, dates, group size, amenities — using Groq (Llama 3.3 70B) with a rule-based fallback when no API key is set
- **Searches 11,000 hotel and flight records by meaning** — not exact keywords, but semantic similarity using vector embeddings and Pinecone
- **Generates a friendly travel recommendation** — the LLM writes a human-readable summary grounded in actual search results, not hallucinated data
- **Protects the API** — API key authentication, rate limiting (50 req/min), and in-memory caching for repeated queries
- **Measures retrieval quality with a 25-query evaluation suite** — precision@k, recall@k, MRR, and hit rate — built from programmatic ground truth, not guesswork. Hotels score 1.0 precision, flights score 0.88. All quality checks pass
- **Runs anywhere** — Docker container with one-command local setup, deployed on a self-hosted Hetzner VPS with Nginx reverse proxy

## Why I Built It

Wanted to build something that shows the full RAG pipeline end to end — not just "call an LLM and return the response." This project takes unstructured human conversation, extracts structured data from it, uses that data to search a real vector database, and then feeds the search results back to the LLM for a grounded summary. Every piece connects to the next. Built it to prove I understand how agentic AI pipelines work in production — from raw input to deployed API.

## Tech Stack

| Layer | Technology | Why This Choice |
|---|---|---|
| Language | Python 3.11 | Industry standard for AI/ML pipelines |
| Web Framework | FastAPI | Auto-generates API docs, native Pydantic support, async-ready |
| LLM Provider | Groq (Llama 3.3 70B) | Free tier, fast inference on custom hardware, accurate for entity extraction |
| LLM Orchestration | LangChain | Chains prompt → LLM → parser in one pipeline with LCEL |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free, local, no API key needed, 384-dim vectors — fast and accurate enough |
| Vector Database | Pinecone (Serverless) | Managed cloud vector search with metadata filtering, free tier |
| Data Validation | Pydantic v2 | Typed schemas that auto-validate input and generate API docs |
| Containerisation | Docker + Docker Compose | One-command local setup, identical environment everywhere |
| Deployment | Hetzner + Docker + Nginx | Self-hosted VPS with reverse proxy — full control over the infrastructure |

## Architecture

```
[Group Chat Messages — unstructured text]
        │
        ▼
┌──────────────────────────────────────────┐
│  main.py — FastAPI Server                │
│                                          │
│  1. Verify API key (X-API-Key header)    │
│  2. Rate limit check (50 req/min)        │
│  3. Cache check (SHA-256 hash lookup)    │
│                                          │
│  4. intent_extractor.py                  │
│     └── LangChain + Groq → TravelIntent │
│     └── Fallback: regex + keywords       │
│                                          │
│  5. retriever.py                         │
│     └── embeddings.py → query vector     │
│     └── Pinecone search with filters     │
│     └── Returns top-k hotels + flights   │
│                                          │
│  6. itinerary_generator.py               │
│     └── LLM writes friendly summary      │
│     └── Grounded in search results only  │
│                                          │
│  7. Build ItineraryResponse              │
│  8. Cache result                         │
│  9. Return JSON                          │
└──────────────────────────────────────────┘
        │
        ▼
[JSON Response: extracted intent + hotels + flights + summary + timing]


┌──────────────────────────────────────────┐
│  Retrieval Evaluation (offline)          │
│                                          │
│  build_eval_set.py                       │
│     └── Reads hotels.json + flights.json │
│     └── Builds 25 queries + ground truth │
│     └── Saves eval_queries.json          │
│                                          │
│  run_eval.py                             │
│     └── Runs queries against Pinecone    │
│     └── Compares results vs ground truth │
│     └── Reports Precision, Recall,       │
│         MRR, Hit Rate per query          │
│     └── Saves eval_results.json          │
└──────────────────────────────────────────┘
```

## How To Run Locally

**Prerequisites:** Python 3.11+, Docker (optional), API keys for Groq and Pinecone (both have free tiers).

**Step 1 — Clone the repo:**

```bash
git clone https://github.com/NakuSurrey/agentic-travel-rag-pipeline.git
cd agentic-travel-rag-pipeline
```

**Step 2 — Create `.env` from the template:**

```bash
cp .env.example .env
```

Open `.env` and fill in your actual keys:

```
GROQ_API_KEY=your_actual_groq_key
PINECONE_API_KEY=your_actual_pinecone_key
APP_API_KEY=pick_any_key_for_testing
```

Get a free Groq key at [console.groq.com](https://console.groq.com). Get a free Pinecone key at [app.pinecone.io](https://app.pinecone.io).

**Step 3 — Install dependencies:**

```bash
pip install -r requirements.txt
```

**Step 4 — Generate mock data (first time only):**

```bash
python -m scripts.generate_mock_data
```

**Step 5 — Ingest records into Pinecone (first time only):**

```bash
python -m scripts.ingest_to_pinecone
```

This embeds all 11,000 records and uploads them to your Pinecone index. Takes a few minutes.

**Step 6 — Start the server:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 7 — Test it:**

Open `http://localhost:8000/docs` in your browser. Use the Swagger UI to send a POST request to `/api/v1/plan-trip` with the `X-API-Key` header set to whatever you put in `.env`.

**Alternative — Run with Docker:**

```bash
docker compose up --build
```

This builds the image, loads `.env` at runtime, and starts the server on port 8000.

## Retrieval Evaluation

Built a 25-query evaluation suite that measures whether the vector search actually returns correct results. Ground truth is not hand-picked — it is generated programmatically by applying the exact same filter logic the retriever uses against the raw data files. This means expected IDs are mathematically correct, not human guesses.

**Metrics measured per query:**

| Metric | What it answers |
|---|---|
| Precision@k | Of the 5 results shown, how many are actually relevant? |
| Recall@k | Of all relevant records in the DB, how many appeared in top 5? |
| MRR | Where does the first relevant result appear in the ranked list? |
| Hit Rate@k | Did at least one relevant result show up? |

**Results (25 queries, top_k=5):**

| Category | Precision@5 | MRR | Hit Rate@5 |
|---|---|---|---|
| Hotels | 1.00 | 1.00 | 1.00 |
| Flights | 0.88 | 0.88 | 0.88 |

Hotels scored perfectly — every result returned was relevant, and the first result was always correct. Three flight queries scored 0.0 because zero flights exist in the database at those price points — the evaluation correctly identified this as a limitation rather than a bug.

**Run the evaluation yourself:**

```bash
python scripts/build_eval_set.py    # generates ground truth from data
python scripts/run_eval.py           # runs 25 queries against Pinecone
```

## Key Decisions

- **Groq over OpenAI** — Free tier with fast inference. Llama 3.3 70B is accurate enough for entity extraction and summary generation. Zero cost.
- **Local embeddings over OpenAI embeddings** — `all-MiniLM-L6-v2` runs on your machine with no API key. 384 dimensions instead of 1536 — faster to search, still accurate for travel record matching.
- **temperature=0 for extraction, 0.7 for summaries** — Structured JSON output needs deterministic, predictable results. Friendly travel summaries need natural, varied language. Different jobs need different settings.
- **Rule-based fallback for intent extraction** — If the Groq API key is missing or the service is down, the system still works using regex and keyword matching. Graceful degradation over hard failure.
- **Upsert not insert for Pinecone ingestion** — Makes the ingestion script idempotent. Running it twice updates existing records instead of creating duplicates. Safe to retry on failure.
- **Separate Pinecone queries for hotels and flights** — Each query uses type-specific metadata filters. Keeps results clean and allows independent tuning of top-k per category.
- **Programmatic ground truth over hand-picked** — Evaluation expected IDs are built by filtering raw data with the exact same logic the retriever uses. Zero human error, fully reproducible, and scales to any dataset size.

## What I Learned

- RAG is retrieval first, generation second — the LLM works from retrieved data, not its own imagination
- LangChain LCEL chains prompt → LLM → parser with the pipe operator — data flows left to right
- Vector embeddings capture meaning — similar text produces similar vectors, enabling search by meaning instead of keywords
- Cosine similarity measures the angle between two vectors — 1.0 means identical meaning, 0.0 means unrelated
- Pinecone metadata filtering combines vector similarity with traditional filters — best of both search methods
- Pydantic models serve triple duty — input validation, output serialization, and auto-generated API docs
- Environment variables keep secrets out of code — `.env` for local, server `.env` for production, same `os.getenv()` call works both places
- Docker layer caching matters — separate COPY for requirements.txt keeps pip install cached when only code changes
- In-memory rate limiting tracks timestamps per client — filtering old timestamps prevents memory leaks and false rejections
- Graceful degradation is a design choice — non-critical failures return fallback messages instead of crashing the entire request
- Retrieval evaluation separates "does it return results" from "does it return the right results" — precision, recall, MRR, and hit rate each answer a different question
- Programmatic ground truth eliminates human bias from evaluation — apply the exact same filters to the raw data and the expected IDs are mathematically guaranteed correct
