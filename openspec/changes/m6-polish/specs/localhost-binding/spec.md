## ADDED Requirements

### Requirement: ChromaDB Docker port binds to localhost only
The Docker Compose configuration SHALL bind ChromaDB's port to 127.0.0.1 only, preventing access from other machines on the network.

#### Scenario: Port binding in docker-compose.yml
- **WHEN** Docker Compose is configured
- **THEN** the ChromaDB port mapping SHALL be `127.0.0.1:${CHROMADB_PORT:-8000}:8000`
- **AND** ChromaDB SHALL NOT be accessible from other machines on the local network
