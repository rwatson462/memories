## Why

With the project skeleton in place (M1), we need the foundational layers that all feature code depends on: configuration loading, data models, and the vector store abstraction with its ChromaDB implementation. These are the building blocks that the service layer (M3) and CLI (M4) will consume.

## What Changes

- Configuration module using pydantic-settings to load env vars with defaults
- Pydantic models for all request/response data shapes and enums (DecayPolicy, OutputFormat)
- VectorStore Protocol defining the abstract interface for vector storage operations
- ChromaDB adapter implementing the VectorStore Protocol via HTTP client

## Capabilities

### New Capabilities
- `configuration`: Environment-based configuration loading via pydantic-settings
- `data-models`: Pydantic models and enums for memory data shapes
- `vector-store-protocol`: Abstract VectorStore interface as a Python Protocol
- `chromadb-adapter`: ChromaDB implementation of the VectorStore Protocol

### Modified Capabilities
(none)

## Impact

- Creates `src/memories/config.py`, `src/memories/models.py`, `src/memories/stores/vector_store.py`, `src/memories/stores/chromadb_adapter.py`
- Establishes the VectorStore Protocol that all future storage operations depend on
- ChromaDB adapter is the first component that requires a running ChromaDB instance
