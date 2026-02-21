## ADDED Requirements

### Requirement: VectorStore Protocol defines the storage interface
The system SHALL define a VectorStore Protocol with methods: store, get, search, delete, update_metadata, count, heartbeat.

#### Scenario: Protocol is implementable
- **WHEN** a class implements all methods of the VectorStore Protocol
- **THEN** it SHALL pass runtime Protocol checks (structural subtyping)

### Requirement: store method persists a document
The VectorStore store method SHALL accept id (str), content (str), and metadata (dict) and persist them.

#### Scenario: Storing a document
- **WHEN** store(id="abc", content="test memory", metadata={"agent": "claude"}) is called
- **THEN** the document SHALL be retrievable via get("abc")

### Requirement: search method returns similar documents
The VectorStore search method SHALL accept query (str), n_results (int), and where (dict, optional) and return matching documents ordered by similarity.

#### Scenario: Semantic search
- **WHEN** search(query="python preferences", n_results=5) is called
- **THEN** results SHALL be ordered by embedding similarity to the query
- **AND** each result SHALL include id, content, metadata, and a distance/similarity score

#### Scenario: Filtered search
- **WHEN** search(query="python", n_results=5, where={"agent": "claude", "deleted": false}) is called
- **THEN** only documents matching ALL where conditions SHALL be returned

### Requirement: get method retrieves by ID
The VectorStore get method SHALL return a single document by ID, or None if not found.

#### Scenario: Get existing document
- **WHEN** get(id="abc") is called for an existing document
- **THEN** the document's id, content, and metadata SHALL be returned

#### Scenario: Get non-existent document
- **WHEN** get(id="nonexistent") is called
- **THEN** None SHALL be returned

### Requirement: delete method removes a document
The VectorStore delete method SHALL permanently remove a document by ID.

#### Scenario: Delete existing document
- **WHEN** delete(id="abc") is called
- **THEN** get("abc") SHALL return None afterward

### Requirement: update_metadata method modifies metadata
The VectorStore update_metadata method SHALL update specific metadata keys on an existing document without affecting content or other metadata.

#### Scenario: Update single metadata key
- **WHEN** update_metadata(id="abc", metadata={"deleted": true}) is called
- **THEN** the document's "deleted" metadata SHALL be true
- **AND** all other metadata keys SHALL remain unchanged

### Requirement: heartbeat method checks connectivity
The VectorStore heartbeat method SHALL return True if the backend is reachable, False otherwise.

#### Scenario: Backend is reachable
- **WHEN** heartbeat() is called with a running backend
- **THEN** True SHALL be returned

#### Scenario: Backend is unreachable
- **WHEN** heartbeat() is called with the backend down
- **THEN** False SHALL be returned
