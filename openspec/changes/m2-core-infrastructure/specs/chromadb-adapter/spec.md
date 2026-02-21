## ADDED Requirements

### Requirement: ChromaDB adapter connects via HTTP client
The ChromaDBAdapter SHALL connect to ChromaDB using the HTTP client mode (not embedded), using the host and port from configuration.

#### Scenario: Successful connection
- **WHEN** ChromaDBAdapter is initialized with a valid ChromaDB host and port
- **THEN** it SHALL connect to the ChromaDB server via HTTP
- **AND** it SHALL get or create the configured collection name

#### Scenario: Connection failure
- **WHEN** ChromaDBAdapter is initialized with an unreachable host
- **THEN** heartbeat() SHALL return False

### Requirement: ChromaDB adapter implements VectorStore Protocol
The ChromaDBAdapter SHALL implement all methods of the VectorStore Protocol using ChromaDB's Python client API.

#### Scenario: Store and retrieve round-trip
- **WHEN** a document is stored via the adapter and then retrieved by ID
- **THEN** the content and metadata SHALL match exactly what was stored

#### Scenario: Search with metadata filter
- **WHEN** multiple documents are stored with different metadata
- **AND** a search is performed with a where filter
- **THEN** only documents matching the filter SHALL appear in results

#### Scenario: Metadata update
- **WHEN** update_metadata is called to set deleted=true on a document
- **THEN** a subsequent get SHALL show deleted=true in metadata
- **AND** a search with where={"deleted": false} SHALL exclude that document

### Requirement: ChromaDB adapter handles compound filters
The ChromaDBAdapter SHALL support combining multiple metadata filters using ChromaDB's `$and` operator.

#### Scenario: Multiple filter conditions
- **WHEN** search is called with where={"agent": "claude", "project": "foo", "deleted": false}
- **THEN** the adapter SHALL construct a ChromaDB `$and` query combining all conditions
- **AND** only documents matching ALL conditions SHALL be returned
