## 1. Test Configuration

- [x] 1.1 Create `tests/conftest.py` — Define fixtures: `settings` (test Settings with unique collection name), `chromadb_adapter` (real ChromaDBAdapter connecting to localhost ChromaDB, creates a test collection, tears it down after test), `mock_vector_store` (MagicMock satisfying VectorStore Protocol), `memory_service` (MemoryService with mock_vector_store and settings), `real_memory_service` (MemoryService with real chromadb_adapter and settings). Add pytest marker registration for `integration`.

## 2. Decay Unit Tests

- [x] 2.1 Create `tests/test_decay.py` — Test `compute_confidence` for stable policy: verify confidence=1.0 at ages 0, 360, 720, and 10000 hours. Test contextual policy: verify confidence at age 0 (1.0), half of half-life (0.5), full half-life (0.0), beyond half-life (0.0). Test reinforceable policy: verify decay from last_reinforced_at, verify fallback to created_at when never reinforced. Test rounding to 4 decimal places.

## 3. Service Unit Tests

- [x] 3.1 Create `tests/test_memory_service.py` — Test create_memory: verify VectorStore.store called with UUID and correct metadata, verify MemoryResponse returned with confidence=1.0. Test search_memories: configure mock to return results with varying ages, verify confidence filtering (results below min_confidence excluded), verify deleted=false always in where filter, verify tag filters added when non-empty. Test get_memory: found case, not found case (returns None), deleted case (returns deleted=true). Test reinforce_memory: valid reinforceable case, stable case (InvalidOperationError), contextual case (InvalidOperationError), not found case. Test delete_memory: success case, already deleted case, not found case. Test get_status: healthy and unhealthy cases.

## 4. Adapter Integration Tests

- [x] 4.1 Create `tests/test_chromadb_adapter.py` — *(Requires running ChromaDB)* Test store/get round-trip: store a document, get by ID, verify content and metadata match. Test search: store multiple documents, search by query, verify results ordered by relevance. Test search with where filter: store documents with different metadata, search with filter, verify only matching documents returned. Test compound filter with $and: multiple filter conditions, verify correct construction. Test update_metadata: update a single key, verify other keys unchanged. Test delete: delete document, verify get returns None. Test heartbeat: verify returns True with running ChromaDB. Test count: store N documents, verify count returns N.

## 5. CLI End-to-End Tests

- [x] 5.1 Create `tests/test_cli.py` — *(Requires running ChromaDB)* Test create command: invoke via CliRunner, verify exit code 0, parse JSON output, verify all fields present. Test search command: create a memory first, search for it, verify it appears in results. Test get command: create a memory, get by ID, verify output. Test get non-existent: verify exit code 1 and error JSON on stderr. Test reinforce command: create a reinforceable memory, reinforce it, verify confidence=1.0. Test reinforce stable memory: verify exit code 1 and error. Test delete command: create and delete, verify output. Test status command: verify healthy response with ChromaDB running. Test --format text: verify non-JSON output for at least one command.
