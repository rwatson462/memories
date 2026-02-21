## ADDED Requirements

### Requirement: memory create stores a new memory
The `memory create` command SHALL accept content as a positional argument and store it as a new memory via the service layer.

#### Scenario: Create with all options
- **WHEN** `memory create "User prefers Python" --agent claude --personality engineer --project my-project --type preference --global --decay stable` is executed
- **THEN** stdout SHALL contain a JSON object with id, content, agent, personality, project, type, global, decay_policy, confidence (1.0), and created_at
- **AND** exit code SHALL be 0

#### Scenario: Create with minimal arguments
- **WHEN** `memory create "A simple observation"` is executed
- **THEN** the memory SHALL be stored with default values (agent="", personality="", project="", type="", global=false, decay_policy=stable)
- **AND** stdout SHALL contain a JSON object with all fields

#### Scenario: Create with text output
- **WHEN** `memory create "test" --format text` is executed
- **THEN** stdout SHALL contain human-readable formatted output (not JSON)

### Requirement: memory search performs semantic search
The `memory search` command SHALL accept a query as a positional argument and return semantically similar memories.

#### Scenario: Basic search
- **WHEN** `memory search "python CLI tools"` is executed
- **THEN** stdout SHALL contain a JSON object with "results" (array of memory objects with similarity scores) and "count" (integer)
- **AND** each result SHALL include confidence and similarity fields
- **AND** exit code SHALL be 0

#### Scenario: Filtered search
- **WHEN** `memory search "preferences" --agent claude --project my-project --limit 5 --min-confidence 0.5` is executed
- **THEN** results SHALL be filtered to only memories matching agent="claude" and project="my-project"
- **AND** at most 5 results SHALL be returned
- **AND** no result SHALL have confidence below 0.5

#### Scenario: Search with no results
- **WHEN** `memory search "nonexistent topic"` returns no matches
- **THEN** stdout SHALL contain `{"results": [], "count": 0}`
- **AND** exit code SHALL be 0

### Requirement: memory get retrieves a memory by ID
The `memory get` command SHALL accept a memory ID and return it.

#### Scenario: Get existing memory
- **WHEN** `memory get <valid-id>` is executed
- **THEN** stdout SHALL contain a JSON object with the memory's fields and computed confidence
- **AND** exit code SHALL be 0

#### Scenario: Get non-existent memory
- **WHEN** `memory get <invalid-id>` is executed
- **THEN** stderr SHALL contain `{"error": "Memory not found"}`
- **AND** exit code SHALL be 1

### Requirement: memory reinforce resets decay timer
The `memory reinforce` command SHALL reinforce a reinforceable memory.

#### Scenario: Reinforce a reinforceable memory
- **WHEN** `memory reinforce <id>` is executed for a reinforceable memory
- **THEN** stdout SHALL contain a JSON object with id, confidence (1.0), and last_reinforced_at
- **AND** exit code SHALL be 0

#### Scenario: Reinforce a stable memory
- **WHEN** `memory reinforce <id>` is executed for a stable memory
- **THEN** stderr SHALL contain a JSON error explaining stable memories cannot be reinforced
- **AND** exit code SHALL be 1

#### Scenario: Reinforce a contextual memory
- **WHEN** `memory reinforce <id>` is executed for a contextual memory
- **THEN** stderr SHALL contain a JSON error explaining contextual memories cannot be reinforced
- **AND** exit code SHALL be 1

### Requirement: memory delete soft-deletes a memory
The `memory delete` command SHALL soft-delete a memory by ID.

#### Scenario: Delete existing memory
- **WHEN** `memory delete <id>` is executed for an existing non-deleted memory
- **THEN** stdout SHALL contain `{"id": "<id>", "deleted": true}`
- **AND** exit code SHALL be 0

#### Scenario: Delete already-deleted memory
- **WHEN** `memory delete <id>` is executed for an already-deleted memory
- **THEN** stderr SHALL contain a JSON error
- **AND** exit code SHALL be 1

### Requirement: memory status reports service health
The `memory status` command SHALL check ChromaDB connectivity and report status.

#### Scenario: Healthy service
- **WHEN** `memory status` is executed with ChromaDB running
- **THEN** stdout SHALL contain a JSON object with status="healthy", chromadb_host, collection, and memory_count
- **AND** exit code SHALL be 0

#### Scenario: Unhealthy service
- **WHEN** `memory status` is executed with ChromaDB unreachable
- **THEN** stderr SHALL contain a JSON object with status="unhealthy" and error details
- **AND** exit code SHALL be 1

### Requirement: All commands support --format flag
Every command SHALL accept a `--format` option with values "json" (default) and "text".

#### Scenario: JSON is default
- **WHEN** any command is executed without `--format`
- **THEN** output SHALL be valid JSON

#### Scenario: Text format
- **WHEN** any command is executed with `--format text`
- **THEN** output SHALL be human-readable formatted text

### Requirement: Errors are JSON on stderr
All error output SHALL be JSON objects written to stderr with an "error" key.

#### Scenario: Service error
- **WHEN** a command encounters a MemoryNotFoundError or InvalidOperationError
- **THEN** stderr SHALL contain `{"error": "<human-readable message>"}`
- **AND** exit code SHALL be 1

#### Scenario: ChromaDB connection error
- **WHEN** a command fails because ChromaDB is unreachable
- **THEN** stderr SHALL contain `{"error": "Cannot connect to ChromaDB at <host>:<port>. Is Docker running?"}`
- **AND** exit code SHALL be 1
