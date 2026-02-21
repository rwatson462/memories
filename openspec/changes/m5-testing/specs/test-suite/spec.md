## ADDED Requirements

### Requirement: Decay computation has full unit test coverage
All three decay policies SHALL be tested with boundary conditions and edge cases.

#### Scenario: Stable policy tests
- **WHEN** tests for the stable decay policy are run
- **THEN** confidence SHALL be verified as 1.0 for ages 0, 360, 720, and 10000 hours

#### Scenario: Contextual policy tests
- **WHEN** tests for the contextual decay policy are run
- **THEN** confidence SHALL be verified at: age 0 → 1.0, age 360 → 0.5, age 720 → 0.0, age 1000 → 0.0

#### Scenario: Reinforceable policy tests
- **WHEN** tests for the reinforceable policy are run
- **THEN** confidence SHALL be verified using last_reinforced_at as reference time
- **AND** behavior without reinforcement SHALL match contextual

#### Scenario: Rounding precision test
- **WHEN** confidence is computed for a non-round age value
- **THEN** the result SHALL be rounded to 4 decimal places

### Requirement: Service tests use mocked VectorStore
MemoryService unit tests SHALL mock the VectorStore Protocol to isolate business logic from ChromaDB.

#### Scenario: Create memory test
- **WHEN** create_memory is called with valid input
- **THEN** the mock VectorStore.store SHALL be called once with correct arguments
- **AND** a MemoryResponse SHALL be returned with confidence=1.0

#### Scenario: Search memory test with confidence filtering
- **WHEN** the mock VectorStore returns 3 results with varying ages
- **THEN** only results with confidence >= min_confidence SHALL be returned

#### Scenario: Get deleted memory test
- **WHEN** the mock VectorStore returns a document with deleted=true
- **THEN** MemoryNotFoundError SHALL be raised

#### Scenario: Reinforce invalid policy test
- **WHEN** reinforce_memory is called for a stable memory
- **THEN** InvalidOperationError SHALL be raised

### Requirement: ChromaDB adapter tests run against real ChromaDB
Adapter tests SHALL use a real ChromaDB instance to validate end-to-end storage behavior.

#### Scenario: Store and get round-trip
- **WHEN** a document is stored via the adapter and retrieved by ID
- **THEN** content and metadata SHALL match exactly

#### Scenario: Search with metadata filter
- **WHEN** documents with different metadata are stored
- **AND** a filtered search is performed
- **THEN** only matching documents SHALL be returned

#### Scenario: Update metadata
- **WHEN** metadata is updated on a document
- **THEN** a subsequent get SHALL reflect the updated metadata

### Requirement: CLI tests validate end-to-end behavior
CLI tests SHALL invoke commands via typer.testing.CliRunner and validate JSON output and exit codes.

#### Scenario: Create and search round-trip
- **WHEN** `memory create` is invoked followed by `memory search`
- **THEN** the created memory SHALL appear in search results

#### Scenario: Error exit codes
- **WHEN** `memory get <invalid-id>` is invoked
- **THEN** exit code SHALL be 1
- **AND** stderr output SHALL contain a JSON error
