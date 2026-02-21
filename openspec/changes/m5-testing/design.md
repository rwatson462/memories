## Context

The test suite needs to cover four layers: pure computation (decay), business logic (service), storage (adapter), and the CLI surface. Each layer has different testing requirements and dependencies.

## Goals / Non-Goals

**Goals:**
- Full coverage of decay computation (all branches, boundary conditions)
- Service logic tested in isolation (mocked VectorStore)
- Adapter verified against real ChromaDB
- CLI commands tested end-to-end with exit code and output validation

**Non-Goals:**
- Performance testing
- Load testing
- 100% line coverage (focus on critical paths and edge cases)

## Decisions

### Test framework: pytest
Standard choice. Use pytest fixtures for setup/teardown, `unittest.mock` for mocking, `freezegun` or manual datetime injection for time-dependent tests.

### Mocking the VectorStore: unittest.mock.MagicMock
Create a MagicMock that satisfies the VectorStore Protocol. Configure return values for each test scenario. This isolates service tests from ChromaDB entirely.

**Alternative considered:** A fake in-memory VectorStore implementation. More realistic but more code to maintain. Mock is sufficient since adapter has its own integration tests.

### ChromaDB test isolation: unique collection per test
Each test that touches ChromaDB uses a unique collection name (e.g., `test_{uuid}`). The conftest fixture creates the collection before the test and deletes it after. This avoids cross-test contamination without needing to restart ChromaDB.

### CLI testing: typer.testing.CliRunner
Typer provides a CliRunner that invokes commands in-process (no subprocess). This is fast and captures stdout/stderr. Integration tests use a real ChromaDB instance.

### Datetime mocking for decay tests
Pass `datetime` as a parameter to `compute_confidence` or use `freezegun` to mock `datetime.now()`. The function-parameter approach is cleaner — the decay function already takes `created_at` and `last_reinforced_at` as inputs, so we just need to control "now". Add an optional `now` parameter to `compute_confidence` with a default of `datetime.utcnow()`.

## Risks / Trade-offs

- [Risk] Integration tests fail if ChromaDB isn't running → Mark integration tests with `@pytest.mark.integration` so they can be skipped in environments without Docker.
- [Trade-off] CliRunner runs in-process (shares Python state) → Faster but less isolated than subprocess. Acceptable for this project's scale.
