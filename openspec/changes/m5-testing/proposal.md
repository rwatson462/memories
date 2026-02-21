## Why

With all feature code complete (M1–M4), we need automated tests to lock down behavior and prevent regressions. The test suite covers all three layers: decay computation (pure unit tests), service logic (unit tests with mocked VectorStore), adapter integration (tests against real ChromaDB), and CLI commands (end-to-end via Typer's test runner).

## What Changes

- Test fixtures: ChromaDB test collection, service instance, mocked VectorStore
- Unit tests for decay computation (all policies, boundary conditions)
- Unit tests for MemoryService (mocked VectorStore)
- Integration tests for ChromaDB adapter (real ChromaDB)
- CLI end-to-end tests via typer.testing.CliRunner

## Capabilities

### New Capabilities
- `test-suite`: Automated test coverage across all application layers

### Modified Capabilities
(none)

## Impact

- Creates `tests/conftest.py`, `tests/test_decay.py`, `tests/test_memory_service.py`, `tests/test_chromadb_adapter.py`, `tests/test_cli.py`
- Integration and CLI tests require a running ChromaDB instance
- Establishes the test patterns for all future development
