## Why

With configuration, models, and the ChromaDB adapter in place (M2), we need the business logic layer that orchestrates memory operations. This is the brain of the application — it handles storing memories with proper metadata, computing confidence via decay formulas, filtering search results, enforcing soft-delete, and validating reinforce operations. The CLI (M4) will be a thin wrapper over this layer.

## What Changes

- Decay computation module with confidence calculation for all three policies
- MemoryService class orchestrating all memory operations (create, search, get, reinforce, delete, status)
- Lazy confidence computation at query time
- Soft-delete enforcement on all read operations
- Minimum confidence filtering on search results

## Capabilities

### New Capabilities
- `decay-computation`: Confidence calculation based on decay policies and timestamps
- `memory-operations`: Full CRUD + search + reinforce business logic

### Modified Capabilities
(none)

## Impact

- Creates `src/memories/services/decay.py` and `src/memories/services/memory_service.py`
- Depends on: VectorStore Protocol (M2), Models (M2), Config (M2)
- All ChromaDB interaction goes through the VectorStore abstraction — service never imports chromadb directly
