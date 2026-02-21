## 1. Error Message Improvements

- [x] 1.1 Update `src/memories/services/memory_service.py` — Ensure MemoryNotFoundError includes the memory ID in its message: `Memory '<id>' not found`. Ensure InvalidOperationError messages are descriptive: include the decay policy name and why the operation is invalid. Ensure delete of already-deleted memory gives specific message: `Memory '<id>' is already deleted`.
- [x] 1.2 Update `src/memories/cli.py` — In the exception handler for ChromaDB connection errors, include the configured host and port in the error message: `Cannot connect to ChromaDB at {host}:{port}. Is Docker running?`.

## 2. Text Output Formatter

- [x] 2.1 Implement text formatting in `src/memories/cli.py` — Update the `output_text` helper function to produce clean key-value output for single memories (padded alignment) and multi-result search output (memories separated by blank lines, summary count line at the end: "Found N memories").

## 3. Security Hardening

- [x] 3.1 Update `docker-compose.yml` — Change port mapping from `${CHROMADB_PORT:-8000}:8000` to `127.0.0.1:${CHROMADB_PORT:-8000}:8000` to bind ChromaDB to localhost only.

## 4. Verification

- [x] 4.1 Manually verify error messages: try `memory get nonexistent-id`, try commands with ChromaDB stopped, try `memory reinforce` on a stable memory. Confirm error messages are actionable and include context.
- [x] 4.2 Manually verify text output: run `memory create "test" --format text`, `memory search "test" --format text`, `memory status --format text`. Confirm output is human-readable and not JSON.
- [x] 4.3 Verify ChromaDB is not accessible from other machines (or confirm `docker compose ps` shows 127.0.0.1 binding).
