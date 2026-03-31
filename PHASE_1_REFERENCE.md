# PHASE 1 REFERENCE — Foundation Layer (Complete Teach-Through)

---

## Files built in this phase

| File | Purpose |
|---|---|
| `app/config.py` | Loads all configuration (API keys, model names, server settings) from environment variables via `dotenv`. Every other file depends on this. |
| `app/models.py` | Defines Pydantic data models: `TravelIntent`, `ChatRequest`, `ItineraryHotel`, `ItineraryFlight`, `ItineraryResponse`. These are the contracts between all parts of the system. |
| `app/intent_extractor.py` | Takes raw group chat messages and extracts structured travel intent. Uses LangChain + Groq (Llama 3.1) when API key is available, falls back to regex/keyword extraction when not. |
| `app/embeddings.py` | Converts text into 384-dimensional vectors using sentence-transformers (local, free). Contains `record_to_text` (record → sentence), `intent_to_query` (intent → search query), `embed_text` (text → vector). |
| `scripts/generate_mock_data.py` | Generates 5,500 hotel + 5,500 flight records (11,000 total) with realistic attributes. |
| `data/sample_chats.json` | 5 example group chats covering different travel scenarios (beach, mountain, city, adventure, cultural). |
| `data/hotels.json` | 5,500 generated hotel records. |
| `data/flights.json` | 5,500 generated flight records. |
| `.env` / `.env.example` | Environment variable files. `.env` holds real keys (gitignored). `.env.example` is a template for other developers. |
| `.gitignore` | Prevents `.env`, `__pycache__`, and other non-essential files from being committed to Git. |

---

## Architecture overview

```
Group Chat Text (unstructured)
        │
        ▼
┌──────────────────────┐
│  Intent Extractor    │  ← LangChain + Groq (Llama 3.1)
│  (app/intent_        │     Reads chat, outputs structured JSON:
│   extractor.py)      │     budget, dates, vibe, amenities
└──────────┬───────────┘
           │ TravelIntent object
           ▼
┌──────────────────────┐
│  Embeddings Layer    │  ← sentence-transformers (local, free)
│  (app/embeddings.py) │     Converts intent → vector (list of numbers)
└──────────┬───────────┘
           │ query vector
           ▼
┌──────────────────────┐
│  Pinecone Vector DB  │  ← Cloud vector database
│  (app/retriever.py)  │     Finds most similar hotels/flights
└──────────┬───────────┘
           │ top-k matches
           ▼
┌──────────────────────┐
│  FastAPI Server      │  ← Exposes /itinerary endpoint
│  (app/main.py)       │     Orchestrates the full pipeline
└──────────────────────┘
           │
           ▼
     JSON Response (hotels + flights + extracted intent)
```

---

## Tech stack choices and why

**Groq (free tier, Llama 3.1 70B)** — The LLM that reads the chat and extracts structured data. Free, fast (runs on custom hardware for high tokens-per-second), and Llama 3.1 70B is accurate enough for entity extraction. Chosen over OpenAI because it costs $0.

**sentence-transformers (all-MiniLM-L6-v2)** — Runs locally on your machine. Turns text into a vector (a list of 384 numbers) that captures the meaning of the text. Free, offline, no API key needed. Chosen over OpenAI embeddings because it's free and produces smaller vectors (384 vs 1536 dimensions) which are faster to search while still accurate enough for our use case.

**Pinecone** — Cloud database that stores vectors and finds the most similar ones fast. When we send it the vector for "beach destination under $1500," it returns the hotel/flight records whose vectors are closest in meaning. Chosen because it's in the project spec.

**FastAPI** — Python web framework for creating HTTP endpoints. Fast, auto-generates API docs, uses Pydantic natively for input validation.

**Docker** — Packages the entire app into a container so it runs identically on any machine.

---

## FILE-BY-FILE TEACH-THROUGH

---

### FILE 1: `app/config.py`

**Purpose:** Load settings from environment variables so no secret keys are hardcoded in our code.

#### Line-by-line breakdown

**`import os`** — Gives access to `os.getenv()`, which reads values from the operating system's environment variables. Environment variables are key-value pairs that exist outside your code, in the shell or system that runs your program. We use them to store secrets like API keys so they never appear in source code.

**`from dotenv import load_dotenv`** — `dotenv` is a library that reads a file called `.env` in your project root and loads its contents into the environment. Without this, you'd have to manually set every variable in your terminal before running the app.

**`load_dotenv()`** — Executes the loading. Finds `.env`, reads each line (like `GROQ_API_KEY=abc123`), puts that key-value pair into the environment. If there's no `.env` file, it does nothing — no crash, no error. It silently moves on.

**`GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")`** — Reads the value of `GROQ_API_KEY` from the environment. Step by step: (1) look in the environment for a variable named `GROQ_API_KEY`. (2) If found, return that value. (3) If not found, return the default — the empty string `""`. The `: str` is a type hint telling developers and IDEs this variable holds a string. It does not enforce anything at runtime.

**Why `""` as default instead of no default?** Without the second argument, `os.getenv` returns `None` when the key is missing. `None` is a different type than a string. Later in the code, when we check `if GROQ_API_KEY:` to decide LLM vs fallback, both `""` and `None` evaluate to `False`. But `""` stays a string type. This avoids type errors downstream if any code tries to use it as a string (like passing it to an API client). It keeps things predictable.

**`LLM_MODEL`** — Same pattern. Defaults to `"llama-3.1-70b-versatile"`, the model name Groq uses for Llama 3.1 70B.

**`PORT: int = int(os.getenv("PORT", "8000"))`** — `os.getenv` always returns a string. A port number needs to be an integer. `int()` converts `"8000"` → `8000`.

#### The no-.env-file chain (graceful fallback)

No `.env` file → `load_dotenv()` does nothing → `os.getenv("GROQ_API_KEY", "")` returns `""` → in `intent_extractor.py`, `if GROQ_API_KEY:` evaluates to `False` (empty string is falsy) → system routes to rule-based fallback → app keeps running. Three files cooperating: `config.py` provides the value, `intent_extractor.py` checks the value, `models.py` defines the output shape regardless of which path ran.

#### Connection summary

This file talks to every other file in the app. Every module imports specific values from here (`from app.config import GROQ_API_KEY`). If you deleted this file, every other file would crash on startup with an `ImportError`.

#### Interview question

**Q:** "Why not just hardcode the API key in your Python file?"
**A:** Hardcoding secrets in source code is a security risk. If the code gets pushed to GitHub, anyone can see and use your key. Environment variables keep secrets separate from code. The `.env` file is added to `.gitignore` so it never gets committed. The `.env.example` file shows other developers what variables they need to set, without exposing real values.

---

### FILE 2: `app/models.py`

**Purpose:** Defines the shape of every piece of data that moves through the system using Pydantic.

#### What is Pydantic?

A Python library that lets you define what a piece of data should look like (what fields it has, what types those fields are) and automatically validates it. If someone sends `budget_per_person: "hello"` instead of a number, Pydantic catches that and returns an error. Without this file, bad data could flow through the system silently and cause confusing failures later.

#### Key model: TravelIntent

```python
class TravelIntent(BaseModel):
    destination: Optional[str] = Field(None, description="Preferred destination or region")
    vibe: Optional[str] = Field(None, ...)
    budget_per_person: Optional[float] = Field(None, ...)
    check_in: Optional[str] = Field(None, ...)
    check_out: Optional[str] = Field(None, ...)
    group_size: Optional[int] = Field(None, ...)
    amenities: list[str] = Field(default_factory=list, ...)
    notes: Optional[str] = Field(None, ...)
```

**`class TravelIntent(BaseModel)`** — Creates a new data class inheriting from Pydantic's `BaseModel`. Gives it automatic validation, serialization (converting to JSON), and deserialization (converting from JSON).

**`Optional[str]`** — The field can be either a string or `None`. Used because a group chat might not mention every field. Someone might talk about budget but never mention dates.

**Why `Optional[float]` for budget instead of required `float`?** If someone's chat says "let's go to Bali, somewhere beachy with a pool" — they never mentioned a budget. If `budget_per_person` was required `float`, Pydantic would reject the data or the LLM would be forced to invent a number. By making it `Optional[float]`, we say: "capture it as a float if mentioned, leave as `None` if not." Later in the retriever, we check: if budget is `None`, skip the budget filter. If it's a number, filter results under that number.

**`Field(None, description="...")`** — Sets the default value (`None`) and adds a description for auto-generated API docs. If you just wrote `destination: Optional[str] = None`, it would still work but you'd lose the documentation.

**`amenities: list[str] = Field(default_factory=list)`** — `default_factory=list` means "every time a new TravelIntent is created without specifying amenities, create a fresh empty list `[]`." We use `default_factory` instead of `default=[]` because using a mutable default (like a list) directly is a known Python bug — all instances would share the same list object. One instance adding to the list would affect all other instances.

#### Other models

**`ChatRequest`** — What the user sends to the API. Contains `messages` (the group chat) and `top_k` (how many results to return, defaults to 5).

**`ItineraryHotel` / `ItineraryFlight`** — Shape of each result. Each includes a `score` field — the relevance score from Pinecone's vector search. Higher score = closer match in meaning.

**`ItineraryResponse`** — Full response bundling extracted intent + matched hotels + matched flights + `processing_time_ms` to prove the pipeline runs under 800ms.

#### Connection summary

This file does not import from any other project file. It's self-contained. But almost every other file imports from it. `intent_extractor.py` imports `TravelIntent`. `main.py` will import `ChatRequest` and `ItineraryResponse`. `embeddings.py` uses `TravelIntent` indirectly via `intent_to_query()`. If you deleted `models.py`, every other file crashes on import.

#### Interview question

**Q:** "What is Pydantic and why did you use it?"
**A:** Pydantic is a data validation library for Python. You define classes with typed fields, and Pydantic automatically validates incoming data against those types. If someone sends `budget_per_person: "hello"`, it raises a clear error. I used it because FastAPI is built on top of Pydantic — the request and response models automatically become the API's input validation and documentation. It also gives us `.model_json_schema()` which we pass to the LLM so it knows what JSON structure to output.

---

### FILE 3: `app/intent_extractor.py`

**Purpose:** Takes a list of chat messages and outputs a clean `TravelIntent` object with structured fields.

Two extraction strategies:
1. **LLM-based** — sends chat to Groq's Llama 3.1 via LangChain. Used when `GROQ_API_KEY` is set.
2. **Rule-based fallback** — regex + keyword matching. Used when no API key is set.

This is the **graceful fallback pattern**: if your API key expires, rate limit hits, or you're offline — the app still works.

#### Section 1: The prompt template

```python
EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a travel-planning assistant...{schema}..."),
    ("human", "Group chat:\n{chat_text}"),
])
```

**`ChatPromptTemplate.from_messages`** — A LangChain class. A prompt template is a reusable message structure with placeholder variables (`{schema}` and `{chat_text}`). Every time we call the chain, LangChain fills in those placeholders with actual values.

**The `"system"` message** — Instructions to the LLM about how to behave. It reads this before seeing the user's chat. We tell it: output JSON only, use our specific schema, use specific field values, set missing fields to `null`, don't wrap output in markdown code fences (because that would break our JSON parser).

**`{schema}`** — Gets replaced at runtime with the actual JSON schema of `TravelIntent`, generated by `TravelIntent.model_json_schema()`. If you add a new field to `TravelIntent`, the LLM automatically learns about it because the schema updates itself.

**The `"human"` message** — The actual chat transcript the LLM processes alongside the system instructions.

#### Section 2: LLM extraction function

```python
def _extract_with_llm(chat_text: str) -> TravelIntent:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0, max_tokens=1024)
    parser = JsonOutputParser(pydantic_object=TravelIntent)
    chain = EXTRACTION_PROMPT | llm | parser
    result = chain.invoke({"schema": SCHEMA_STR, "chat_text": chat_text})
    return TravelIntent(**result)
```

**`from langchain_groq import ChatGroq` (inside the function)** — This import is inside the function, not at the top of the file. Why? If someone runs the app without `langchain-groq` installed and has no Groq key, the app still loads fine — it uses the fallback. If this import was at the top, the entire file would crash on import even if you never call this function.

**`ChatGroq(...)`** — Creates a connection to Groq's API. A LangChain "chat model" object.
- `model=LLM_MODEL` — from `config.py`, defaults to `"llama-3.1-70b-versatile"`
- `temperature=0` — controls randomness. `0` = most deterministic, predictable output
- `max_tokens=1024` — max response length. Our JSON is small, 1024 is plenty.

**Why `temperature=0` matters for our pipeline:** Our pipeline needs the LLM to output valid, parseable JSON every single time. The JSON must match the exact `TravelIntent` schema — correct field names, correct types, correct values like `"beach"` not `"beachy vibes"`. With `temperature=0`, the LLM picks the most probable next token at every step. Same output for same input. With `temperature=1`, the model introduces randomness — might output `"vibe": "beachy"` instead of `"beach"`, or add chatty text before the JSON, or wrap JSON in code fences. Any of those breaks the `JsonOutputParser`. For data extraction, creativity is the enemy of reliable structured output.

**What is a token?** The smallest unit of text the model generates — usually a word or part of a word.

**`parser = JsonOutputParser(pydantic_object=TravelIntent)`** — Takes raw text from the LLM and converts it into a Python dictionary matching the `TravelIntent` schema. If LLM returns invalid JSON, the parser raises an error.

**`chain = EXTRACTION_PROMPT | llm | parser`** — Core LangChain concept: chaining with the pipe operator. Data flows left to right:
1. `EXTRACTION_PROMPT` fills in template with variables → produces formatted message
2. `| llm` sends message to Groq → gets back raw text (JSON)
3. `| parser` converts raw text → Python dictionary

This is called **LCEL (LangChain Expression Language)**. It's how LangChain connects components into a pipeline.

**`chain.invoke({"schema": SCHEMA_STR, "chat_text": chat_text})`** — Runs the chain. The dictionary provides values for the `{schema}` and `{chat_text}` placeholders.

**`return TravelIntent(**result)`** — Parser returns a dictionary. `**` unpacks it into keyword arguments. `TravelIntent(**{"vibe": "beach", "budget_per_person": 1500})` becomes `TravelIntent(vibe="beach", budget_per_person=1500)`. Pydantic validates the data one more time on creation.

#### Section 3: Rule-based fallback

Uses regex (regular expressions — pattern-matching rules for text) and keyword counting:
- `_detect_vibe(text)` — counts keyword hits per vibe category, highest wins
- `BUDGET_PATTERN` — regex for dollar signs followed by numbers ($1500, $3,000.00)
- `_extract_rule_based()` — runs all patterns, counts unique usernames as `group_size`, collects amenity keywords

#### Section 4: Public entry point

```python
def extract_intent(messages: list[dict]) -> TravelIntent:
    chat_text = _flatten_chat(messages)
    if GROQ_API_KEY:
        return _extract_with_llm(chat_text)
    else:
        return _extract_rule_based(chat_text)
```

Only function other files call. Flattens messages to text, picks strategy based on API key existence.

#### Connection summary

- Imports from `app.models`: `TravelIntent` (output type)
- Imports from `app.config`: `GROQ_API_KEY`, `LLM_MODEL`
- Called by: `app/main.py` (FastAPI server calls `extract_intent()`)
- Output feeds into: `app/embeddings.py` → `intent_to_query()` converts `TravelIntent` into search query string

If deleted, entire pipeline breaks — nothing to extract meaning from chat.

#### Interview question

**Q:** "Explain the LangChain chain you built. What does `EXTRACTION_PROMPT | llm | parser` actually do?"
**A:** It's a LangChain Expression Language pipeline. Data flows left to right. The prompt template fills in placeholder variables with the actual schema and chat text, producing a formatted message. That message gets sent to the Groq LLM which returns raw text — specifically, JSON. The JSON output parser takes that raw text and converts it into a validated Python dictionary matching my TravelIntent schema. The pipe operator connects these three components so calling `.invoke()` on the chain runs all three steps in sequence.

---

### FILE 4: `app/embeddings.py`

**Purpose:** Converts text into vectors (lists of 384 numbers that represent meaning). This is the foundation of how RAG works.

#### What is a vector in this context?

A list of 384 numbers. Example: `[0.023, -0.158, 0.441, ..., 0.072]`. Each number represents one dimension of meaning. The embedding model (a small neural network running locally) reads text and outputs these numbers. Texts with similar meanings produce vectors that are close together. "Beachfront resort in Cancun" and "oceanside hotel in Tulum" would produce very similar vectors.

#### Line-by-line breakdown

**`@lru_cache(maxsize=1)` + `get_model()`** — `@lru_cache` is a decorator (a function that wraps another function to add behavior). First time `get_model()` is called, it runs and stores the result. Every future call returns that stored result without running again. `maxsize=1` = store one result. Why? Loading a model takes seconds. We only want to load it once, then reuse for every request.

**`SentenceTransformer(EMBEDDING_MODEL)`** — Loads the embedding model into memory. First time downloads ~80MB. After that loads from disk.

**`model.encode(text, normalize_embeddings=True)`** — Takes a string, returns 384 numbers. `normalize_embeddings=True` scales numbers so the vector has a length of 1. Matters because Pinecone uses cosine similarity (a way to measure how similar two vectors are) and normalized vectors make that comparison faster and more accurate.

**`.tolist()`** — Model returns a NumPy array (special data type for numerical computation). Pinecone and JSON need regular Python lists. `.tolist()` converts.

#### `record_to_text(record)` — Why natural language, not raw JSON?

Converts a hotel/flight record (dictionary) into a natural-language sentence. Example: `"Marriott Cancun — a 4-star beach hotel in Cancun. $180.50/night. Rating: 4.2/5. Amenities: Pool, Spa, Beach Access."`

**Why not just embed the raw JSON dictionary as a string?** The embedding model was trained on natural language — sentences, paragraphs, articles. It learned meaning from billions of sentences. When you feed it a sentence, it understands word relationships and produces a meaningful vector.

If you feed it `{"stars": 4, "vibe": "beach", "destination": "Cancun"}`, it sees curly braces, colons, quotation marks — formatting characters it wasn't trained on. The resulting vector would be a poor representation. Same input data, completely different quality of vector. The natural-language version lives in the right "neighborhood" of meaning. The JSON version is noise.

`record_to_text` is a translation layer — converts structured data into the format the embedding model was trained to understand.

#### `intent_to_query(intent)` — Same idea in reverse

Takes a `TravelIntent` and produces a search query sentence like: `"beach destination in or near Cancun under $1500 per person from 2026-03-15 to 2026-03-22 with pool, beach access"`. This gets embedded into a vector, then Pinecone finds records with the closest vectors.

#### Connection summary

- Imports from `app.config`: `EMBEDDING_MODEL`
- Used by `app/retriever.py` (not built yet): calls `embed_text()` for search queries and `record_to_text()` during ingestion
- Depends on: `sentence-transformers` library (local, free)

If deleted, can't convert anything to vectors. No vectors = no similarity search. The entire RAG half of the pipeline dies.

#### Interview question

**Q:** "Why did you use a local embedding model instead of OpenAI's embeddings API?"
**A:** Three reasons. (1) It's free — no per-token cost. (2) It runs offline, so no network latency for embedding and no external service dependency. (3) `all-MiniLM-L6-v2` produces 384-dimensional vectors — smaller and faster to search than OpenAI's 1536 dimensions — while still accurate enough for matching travel records to travel intent. Tradeoff: larger models may capture more nuance, but for this use case the smaller model is sufficient.

---

## Connection map (all files)

```
config.py ──────► intent_extractor.py (reads GROQ_API_KEY, LLM_MODEL)
    │
    └──────────► embeddings.py (reads EMBEDDING_MODEL)

models.py ─────► intent_extractor.py (uses TravelIntent as output type)
    │
    └──────────► embeddings.py (TravelIntent used by intent_to_query)

intent_extractor.py ──► [NEXT: main.py calls extract_intent()]

embeddings.py ─────────► [NEXT: retriever.py calls embed_text(), record_to_text()]
```

---

## Key concepts summary

- **Environment variables + dotenv:** secrets outside code, graceful defaults
- **Pydantic:** typed data validation, auto-generated schemas and docs
- **Optional fields:** capture data if present, None if not, handle gracefully downstream
- **default_factory:** prevents shared mutable default bug with lists
- **LangChain LCEL:** pipe operator chains prompt → LLM → parser
- **temperature=0:** deterministic output, critical for structured extraction
- **Graceful fallback:** LLM path when API key exists, rule-based when it doesn't
- **Embeddings:** text → vector (list of numbers representing meaning)
- **lru_cache:** load expensive resources once, reuse forever
- **Normalization:** scale vectors to length 1 for accurate cosine similarity
- **record_to_text:** translate structured data to natural language before embedding — model was trained on language, not JSON
