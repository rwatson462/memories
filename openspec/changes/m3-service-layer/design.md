## Context

The service layer sits between the CLI (M4) and the VectorStore abstraction (M2). It contains all business logic and never directly depends on ChromaDB — only on the VectorStore Protocol.

## Goals / Non-Goals

**Goals:**
- Pure business logic with no I/O concerns (that's the adapter's job)
- Deterministic decay computation (testable with mocked clocks)
- Clean error types for the CLI to handle

**Non-Goals:**
- Output formatting (CLI's job)
- ChromaDB-specific logic (adapter's job)

## Decisions

### Decay module: pure functions
The decay module (`decay.py`) exposes a single pure function: `compute_confidence(decay_policy, created_at, last_reinforced_at, half_life_hours) -> float`. No classes, no state. This makes it trivially testable.

The formula for contextual and reinforceable is linear decay: `confidence = max(0.0, 1.0 - (age_hours / half_life_hours))`. For reinforceable, `age_hours` is measured from `last_reinforced_at` instead of `created_at`.

**Alternative considered:** Exponential decay. More realistic but harder to reason about and tune. Linear is simpler and the specific curve can be changed later without affecting the interface.

### MemoryService: class with injected dependencies
`MemoryService` takes a `VectorStore` instance and a `Settings` instance in its constructor. This makes it testable with a mock VectorStore and configurable settings.

Methods: `create_memory(data: MemoryCreate) -> MemoryResponse`, `search_memories(query, filters, limit, min_confidence) -> SearchResponse`, `get_memory(id) -> MemoryResponse`, `reinforce_memory(id) -> MemoryResponse`, `delete_memory(id) -> dict`, `get_status() -> dict`.

### Error handling: custom exceptions
Define `MemoryNotFoundError` and `InvalidOperationError` in the service module. The CLI maps these to stderr JSON output and exit code 1. This keeps error semantics in the service layer and formatting in the CLI.

### Where filter construction
The service builds the `where` dict for the VectorStore. It always includes `{"deleted": false}`. Additional filters (agent, personality, project, type, global) are added only when the caller provides non-empty values. The adapter handles wrapping these into ChromaDB's `$and` syntax.

## Risks / Trade-offs

- [Risk] Linear decay may feel too aggressive for short half-lives → Tunable via DECAY_HALF_LIFE_HOURS env var. Can switch to a different curve later without API changes.
- [Trade-off] Custom exceptions vs returning Result types → Exceptions are more Pythonic and simpler for the CLI to catch. Result types are more explicit but add boilerplate.
