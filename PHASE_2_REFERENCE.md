# PHASE 2 REFERENCE — RAG Retrieval Layer (Complete Teach-Through)

---

## Files built in this phase

| File | Purpose |
|---|---|
| `app/retriever.py` | Connects to Pinecone. Two jobs: (1) ingest records as vectors, (2) search for matching hotels/flights by similarity. |
| `scripts/ingest_to_pinecone.py` | One-time script that loads all 11,000 records into Pinecone. Run once before starting the API. |

---

## What is Pinecone?

A cloud-hosted vector database. A regular database stores rows and searches by exact matches (WHERE city = "Cancun"). A vector database stores vectors (lists of numbers) and searches by **similarity** — "find the 5 vectors closest in meaning to this query vector."

Closeness is measured by **cosine similarity** — a math formula comparing the angle between two vectors. Score of 1.0 = identical meaning. Score of 0.0 = completely unrelated.

Each vector in Pinecone has:
- An **ID** (like `"HTL-00001"`)
- A **vector** (384 numbers from our embedding model)
- **Metadata** (extra fields like `type`, `vibe`, `price`, `destination` for filtering)

---

## How RAG search works step by step

1. User sends group chat → `intent_extractor` outputs `TravelIntent(vibe="beach", budget=1500, ...)`
2. `intent_to_query()` converts that to `"beach destination under $1500 per person with pool, beach access"`
3. `embed_text()` converts that sentence to a vector of 384 numbers
4. That vector gets sent to Pinecone with a filter like `type == "hotel"` and `price_per_night <= 1500`
5. Pinecone compares the query vector against all stored vectors, applies the filters, returns the top-k closest matches
6. Repeat for flights
7. Results go back to the user

---

## FILE: `app/retriever.py` — Line-by-line teach-through

### Section 1: Pinecone client setup

**`DIMENSION = 384`** — The number of dimensions our embedding model produces. `all-MiniLM-L6-v2` outputs 384 numbers per vector. When creating the Pinecone index, Pinecone needs to know this. If this number doesn't match the vectors we upload, Pinecone rejects them.

**`get_pinecone_client()`** — Creates a Pinecone client object using the API key from `config.py`. Every Pinecone operation (creating indexes, upserting vectors, querying) goes through this client.

**`get_or_create_index()`** — Step by step:
1. Lists all indexes in your Pinecone account
2. Checks if `"travel-rag"` exists
3. If not, creates it with 384 dimensions, cosine metric, AWS serverless (free tier)
4. Returns a reference to the index

**`metric="cosine"`** — Tells Pinecone to use cosine similarity for comparing vectors. Cosine compares the angle between two vectors. Works best with normalized vectors (which ours are — remember `normalize_embeddings=True` in `embeddings.py`).

**`ServerlessSpec(cloud="aws", region="us-east-1")`** — Pinecone's free tier. Serverless = Pinecone manages infrastructure, no servers to provision.

### Section 2: Ingestion

**`ingest_records(records, batch_size=100)`** — The heavy-lifting function.

**Step 1 — Convert records to sentences:**
```python
texts = [record_to_text(r) for r in records]
```
Calls `record_to_text` from `embeddings.py` for each of 11,000 records. Each dictionary becomes a natural-language sentence.

**Step 2 — Embed all sentences:**
```python
vectors = embed_texts(texts)
```
The embedding model processes all 11,000 sentences in one batch. Batching is faster than one-at-a-time because the model batches computation internally.

**Step 3 — Upsert in batches of 100:**
```python
for i in range(0, len(records), batch_size):
```
Pinecone's API has a size limit per request. Sending all 11,000 at once would cause a runtime error. 100 is a safe, efficient batch size.

**`index.upsert(vectors=batch_vectors)`** — "Upsert" = "insert if the ID doesn't exist, update if it does." If you run the script twice, it overwrites existing vectors with the same IDs instead of creating duplicates or crashing. This makes the script **idempotent** — running it multiple times produces the same result as running it once. Senior developers build idempotent operations because things fail and need to be retried.

**Metadata stored per vector:**
- Hotels: `destination`, `vibe`, `stars`, `price_per_night`, `rating`, `name`, `amenities`
- Flights: `destination`, `destination_vibe`, `origin`, `airline`, `cabin_class`, `price`, `departure_date`, `duration_hours`, `stops`, `rating`
- Both: `type` ("hotel" or "flight"), `text` (first 500 chars of description — Pinecone has a metadata size limit)

These metadata fields are what we filter on during search.

### Section 3: Search

**`_build_filter(intent, record_type)`** — Builds a Pinecone metadata filter dynamically from the extracted intent.

How it works:
1. Starts with `[{"type": {"$eq": record_type}}]` — always filter by hotel or flight
2. Checks each intent field — if not `None`, adds a condition
3. If vibe is `"beach"` → adds `vibe == "beach"`
4. If budget is `1500` → adds `price_per_night <= 1500`
5. Wraps all conditions in `{"$and": conditions}` — all must be true

**This is where `Optional` pays off.** If a chat never mentions budget, `budget_per_person` is `None`. The `if intent.budget_per_person is not None:` check skips that filter. No budget mentioned → no budget filter → results at any price. The system adapts to whatever information is available.

**Pinecone filter syntax:** `$and` = all conditions must be true. `$eq` = equals. `$lte` = less than or equal to.

**`search(intent, top_k=5)`** — The main search function. Step by step:
1. `intent_to_query(intent)` → converts intent to query string
2. `embed_text(query_text)` → converts string to 384-number vector
3. `index.query(...)` for hotels with hotel filter
4. `index.query(...)` for flights with flight filter
5. Returns both sets of results

**`index.query(vector=query_vector, top_k=top_k, include_metadata=True, filter=hotel_filter)`** — The core Pinecone search call. "Compare this query vector against all stored vectors that pass the filter. Return the top 5 closest matches. Include metadata so I can display results."

### Connection summary

- **Imports from `app.config`:** `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`
- **Imports from `app.embeddings`:** `embed_text`, `embed_texts`, `record_to_text`, `intent_to_query`
- **Imports from `app.models`:** `TravelIntent`
- **Called by:** `scripts/ingest_to_pinecone.py` (calls `ingest_records`), `app/main.py` (will call `search`)
- **If deleted:** No way to store or search vectors. The RAG half of the pipeline is gone.

---

## FILE: `scripts/ingest_to_pinecone.py`

Simple runner script.

**`sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))`** — Adds the project root to Python's import path. Without this, `from app.retriever import ingest_records` would fail because Python doesn't know where `app` is when running from `scripts/`.

The rest: loads JSON, calls `ingest_records`, prints timing.

---

## Interview questions

**Q:** "How does your RAG system filter results? What if the user doesn't mention a budget?"
**A:** I use Pinecone's metadata filtering. When I ingest records, I store fields like price, vibe, and destination as metadata alongside each vector. During search, I build a filter dynamically from the extracted intent. If the user mentions a budget, I add a `$lte` condition on price. If they don't, that condition is not added. The system naturally adapts to whatever information the group chat provides.

**Q:** "Why do you upsert in batches of 100?"
**A:** Pinecone's API has a request size limit. Sending all 11,000 vectors at once would exceed that limit and cause a runtime error. Batching at 100 keeps each request within safe limits. Upsert (rather than insert) makes the script idempotent — if we re-run it, vectors get updated instead of duplicated.

**Q:** "What is cosine similarity?"
**A:** A math formula that measures the angle between two vectors. If two vectors point in the same direction, cosine similarity is 1.0 — they have identical meaning. If perpendicular, 0.0 — unrelated. I use it because my vectors are normalized to length 1, and cosine similarity is the most accurate metric for normalized vectors.

---

## Key concepts learned in Phase 2

- **Vector database:** stores vectors and finds similar ones by mathematical distance, not exact matches
- **Cosine similarity:** measures angle between vectors. 1.0 = identical, 0.0 = unrelated. Best for normalized vectors
- **Metadata filtering:** store extra fields alongside vectors, filter results before similarity comparison
- **Batched upsert:** upload vectors in chunks to stay within API limits
- **Idempotency:** upsert means re-running produces the same result — safe to retry on failure
- **Dynamic filter building:** only add filter conditions for intent fields that are not None — system adapts to available information
- **ServerlessSpec:** Pinecone's free tier on AWS, no infrastructure to manage
- **sys.path.insert:** tells Python where to find your packages when running scripts from subdirectories
- **@lru_cache(maxsize=1) recall:** loads the 80MB embedding model once, caches it in memory, every future call returns the cached model instantly instead of reloading from disk

---

## Connection map (cumulative — Phase 1 + Phase 2)

```
config.py ──────► intent_extractor.py (GROQ_API_KEY, LLM_MODEL)
    │
    ├──────────► embeddings.py (EMBEDDING_MODEL)
    │
    └──────────► retriever.py (PINECONE_API_KEY, PINECONE_INDEX_NAME)

models.py ─────► intent_extractor.py (TravelIntent)
    │
    ├──────────► embeddings.py (TravelIntent via intent_to_query)
    │
    └──────────► retriever.py (TravelIntent)

embeddings.py ─► retriever.py (embed_text, embed_texts, record_to_text, intent_to_query)

intent_extractor.py ──► [NEXT: main.py calls extract_intent()]
retriever.py ─────────► [NEXT: main.py calls search()]

scripts/ingest_to_pinecone.py ──► retriever.py (calls ingest_records)
```
