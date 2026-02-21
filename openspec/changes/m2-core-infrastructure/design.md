## Context

M1 established the project skeleton. This milestone builds the four foundational modules that all feature code depends on: configuration, data models, the vector store abstraction, and the ChromaDB adapter. These must be solid because the service layer (M3) and CLI (M4) are built entirely on top of them.

## Goals / Non-Goals

**Goals:**
- Type-safe configuration loading from environment variables
- Pydantic models that enforce data contracts between layers
- A clean VectorStore Protocol that decouples business logic from ChromaDB specifics
- A working ChromaDB adapter that can store, search, and manage documents

**Non-Goals:**
- No business logic (decay, confidence filtering) — that's M3
- No CLI commands — that's M4
- No tests — that's M5 (though manual verification against ChromaDB is expected)

## Decisions

### Configuration: pydantic-settings with env vars
Use `pydantic-settings` BaseSettings class. It reads from environment variables, supports `.env` files, and provides type coercion and validation for free. Configuration is a singleton instantiated at import time.

**Alternative considered:** `python-dotenv` + manual env reading. More boilerplate, no validation.

### Models: Pydantic v2 with strict validation
All data shapes are Pydantic BaseModel classes. This gives us validation on construction, JSON serialization for CLI output, and clear type contracts between layers.

Key models:
- `MemoryCreate` — input for creating a memory (CLI -> Service)
- `MemoryResponse` — output for a single memory (Service -> CLI)
- `SearchResultItem` — MemoryResponse + similarity score
- `SearchResponse` — wrapper with results list and count

### VectorStore: Python Protocol (structural subtyping)
Use `typing.Protocol` to define the VectorStore interface. This enables structural subtyping — any class with the right methods satisfies the Protocol without explicit inheritance. This is more Pythonic than ABC and avoids tight coupling.

Methods: `store(id, content, metadata)`, `get(id) -> dict | None`, `search(query, n_results, where) -> list[dict]`, `delete(id)`, `update_metadata(id, metadata)`, `count() -> int`, `heartbeat() -> bool`.

### ChromaDB adapter: HTTP client mode
Use `chromadb.HttpClient(host, port)` to connect to the Docker-hosted ChromaDB server. The adapter gets-or-creates the collection on initialization.

**Metadata filtering:** ChromaDB supports `where` clauses with `$and` for combining multiple conditions. The adapter wraps multi-key `where` dicts into `{"$and": [{key: value}, ...]}` format when more than one filter key is present.

**Empty string sentinels:** Optional metadata fields (agent, personality, project, type) use empty string `""` as the "not set" value since ChromaDB metadata doesn't support null. When building where filters, the adapter only includes keys that have non-empty values to avoid filtering on sentinels.

## Risks / Trade-offs

- [Risk] ChromaDB `$and` filter syntax may change across versions — Acceptable for now; pin version when stabilizing.
- [Risk] Empty string sentinel for "not set" is unconventional — Document clearly. Alternative (omitting keys) makes filtering inconsistent since ChromaDB can't filter on "key exists."
- [Trade-off] Protocol over ABC means no runtime enforcement of method signatures — Acceptable; type checkers (mypy) catch this statically, and integration tests validate it at runtime.
