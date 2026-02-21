## ADDED Requirements

### Requirement: Create memory stores document with metadata
The MemoryService create method SHALL generate a UUID, set created_at to current time, set confidence to 1.0, set deleted to false, and store the document via the VectorStore.

#### Scenario: Creating a memory with all fields
- **WHEN** create_memory is called with content="User prefers Python", agent="claude", personality="engineer", project="my-project", type="preference", global_=false, decay_policy="stable"
- **THEN** a document SHALL be stored in the VectorStore with a generated UUID
- **AND** metadata SHALL include all provided fields plus created_at (ISO 8601), last_reinforced_at (""), and deleted (false)
- **AND** a MemoryResponse SHALL be returned with confidence=1.0

#### Scenario: Creating a memory with minimal fields
- **WHEN** create_memory is called with only content="test"
- **THEN** defaults SHALL be applied: agent="", personality="", project="", type="", global_=false, decay_policy="stable"

### Requirement: Search memories returns filtered, confidence-scored results
The MemoryService search method SHALL perform semantic search, compute confidence for each result, filter by minimum confidence, and exclude deleted memories.

#### Scenario: Search with no filters
- **WHEN** search_memories is called with query="python preferences"
- **THEN** deleted memories SHALL be excluded (where deleted=false is always applied)
- **AND** each result SHALL have a computed confidence value
- **AND** results below min_confidence SHALL be excluded
- **AND** results SHALL be returned as a SearchResponse with count

#### Scenario: Search with tag filters
- **WHEN** search_memories is called with query="python", agent="claude", project="my-project"
- **THEN** the VectorStore where clause SHALL include: {"agent": "claude", "project": "my-project", "deleted": false}

#### Scenario: Search respects limit
- **WHEN** search_memories is called with limit=5
- **THEN** at most 5 results SHALL be returned

### Requirement: Get memory returns single memory by ID
The MemoryService get method SHALL retrieve a memory by ID, compute its confidence, and return it.

#### Scenario: Get existing non-deleted memory
- **WHEN** get_memory is called with a valid ID for a non-deleted memory
- **THEN** a MemoryResponse SHALL be returned with computed confidence

#### Scenario: Get deleted memory
- **WHEN** get_memory is called with an ID for a soft-deleted memory
- **THEN** an error SHALL be raised (memory not found)

#### Scenario: Get non-existent memory
- **WHEN** get_memory is called with an ID that does not exist
- **THEN** an error SHALL be raised (memory not found)

### Requirement: Reinforce memory resets decay for reinforceable memories only
The MemoryService reinforce method SHALL update last_reinforced_at to the current time, but only for memories with the "reinforceable" decay policy.

#### Scenario: Reinforce a reinforceable memory
- **WHEN** reinforce_memory is called for a memory with decay_policy="reinforceable"
- **THEN** last_reinforced_at SHALL be updated to the current time via VectorStore update_metadata
- **AND** the returned confidence SHALL be 1.0

#### Scenario: Reinforce a stable memory
- **WHEN** reinforce_memory is called for a memory with decay_policy="stable"
- **THEN** an error SHALL be raised indicating stable memories cannot be reinforced

#### Scenario: Reinforce a contextual memory
- **WHEN** reinforce_memory is called for a memory with decay_policy="contextual"
- **THEN** an error SHALL be raised indicating contextual memories cannot be reinforced

### Requirement: Delete memory performs soft-delete
The MemoryService delete method SHALL set the deleted metadata flag to true.

#### Scenario: Delete an existing memory
- **WHEN** delete_memory is called with a valid ID
- **THEN** the VectorStore update_metadata SHALL be called with {"deleted": true}
- **AND** subsequent searches SHALL NOT return this memory

#### Scenario: Delete an already-deleted memory
- **WHEN** delete_memory is called for a memory that is already deleted
- **THEN** an error SHALL be raised

#### Scenario: Delete a non-existent memory
- **WHEN** delete_memory is called with an ID that does not exist
- **THEN** an error SHALL be raised

### Requirement: Status checks ChromaDB health
The MemoryService get_status method SHALL check ChromaDB connectivity and report collection statistics.

#### Scenario: Healthy service
- **WHEN** get_status is called and ChromaDB is reachable
- **THEN** it SHALL return status="healthy", the ChromaDB host, collection name, and total memory count

#### Scenario: Unhealthy service
- **WHEN** get_status is called and ChromaDB is unreachable
- **THEN** it SHALL return status="unhealthy" with an error description
