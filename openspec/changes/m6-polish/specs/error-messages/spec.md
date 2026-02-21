## ADDED Requirements

### Requirement: ChromaDB connection errors include actionable guidance
When ChromaDB is unreachable, error messages SHALL include the host/port being contacted and suggest checking Docker.

#### Scenario: ChromaDB unreachable
- **WHEN** any command fails because ChromaDB is not reachable
- **THEN** stderr SHALL contain `{"error": "Cannot connect to ChromaDB at <host>:<port>. Is Docker running?"}`
- **AND** exit code SHALL be 1

### Requirement: Memory not found errors include the ID
When a memory is not found, the error message SHALL include the requested ID.

#### Scenario: Memory not found
- **WHEN** a get, reinforce, or delete command references a non-existent memory ID
- **THEN** stderr SHALL contain `{"error": "Memory '<id>' not found"}`

### Requirement: Invalid operation errors explain the reason
When an operation is invalid (e.g., reinforcing a stable memory), the error SHALL explain why.

#### Scenario: Reinforce stable memory
- **WHEN** `memory reinforce <id>` is called on a stable memory
- **THEN** stderr SHALL contain `{"error": "Memory has stable decay policy, reinforcement has no effect"}`

#### Scenario: Reinforce contextual memory
- **WHEN** `memory reinforce <id>` is called on a contextual memory
- **THEN** stderr SHALL contain `{"error": "Memory has contextual decay policy, reinforcement is not supported"}`

#### Scenario: Delete already-deleted memory
- **WHEN** `memory delete <id>` is called on an already-deleted memory
- **THEN** stderr SHALL contain `{"error": "Memory '<id>' is already deleted"}`
