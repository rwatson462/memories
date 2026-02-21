## 1. Decay Computation

- [x] 1.1 Create `src/memories/services/decay.py` — Implement `compute_confidence(decay_policy: str, created_at: datetime, last_reinforced_at: datetime | None, half_life_hours: float) -> float`. Handle three branches: stable (always 1.0), contextual (linear decay from created_at), reinforceable (linear decay from last_reinforced_at or created_at if never reinforced). Round to 4 decimal places. Clamp to 0.0 minimum.

## 2. Service Exceptions

- [x] 2.1 Define custom exceptions in `src/memories/services/memory_service.py` (or a separate `exceptions.py`): `MemoryNotFoundError(id: str)` and `InvalidOperationError(message: str)`.

## 3. Memory Service

- [x] 3.1 Create `src/memories/services/memory_service.py` — Implement `MemoryService` class with constructor taking `VectorStore` and `Settings`. Implement `create_memory(data: MemoryCreate) -> MemoryResponse`: generate UUID, build metadata dict (all fields + created_at + last_reinforced_at="" + deleted=false), call VectorStore.store(), return MemoryResponse with confidence=1.0.
- [x] 3.2 Implement `search_memories(query: str, agent: str = "", personality: str = "", project: str = "", type_: str = "", global_: bool | None = None, limit: int = 10, min_confidence: float = 0.3) -> SearchResponse`: build where dict (always include deleted=false, add non-empty filters), call VectorStore.search(), compute confidence for each result via decay module, filter results below min_confidence, return SearchResponse.
- [x] 3.3 Implement `get_memory(id: str) -> MemoryResponse`: call VectorStore.get(), raise MemoryNotFoundError if None or deleted=true, compute confidence, return MemoryResponse.
- [x] 3.4 Implement `reinforce_memory(id: str) -> dict`: call VectorStore.get(), raise MemoryNotFoundError if None or deleted, raise InvalidOperationError if decay_policy is not "reinforceable", call VectorStore.update_metadata() with last_reinforced_at=now, return confirmation with confidence=1.0.
- [x] 3.5 Implement `delete_memory(id: str) -> dict`: call VectorStore.get(), raise MemoryNotFoundError if None, raise InvalidOperationError if already deleted, call VectorStore.update_metadata({"deleted": true}), return confirmation.
- [x] 3.6 Implement `get_status() -> dict`: call VectorStore.heartbeat() and VectorStore.count(), return status dict with health, host, collection, and count.
