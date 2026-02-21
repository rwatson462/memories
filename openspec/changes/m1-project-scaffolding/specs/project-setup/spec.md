## ADDED Requirements

### Requirement: Package is installable via pip
The `memories` package SHALL be installable via `pip install -e .` in development mode and via `pipx install .` for isolated production use.

#### Scenario: Development installation
- **WHEN** a developer runs `pip install -e .` from the project root
- **THEN** the `memory` command SHALL be available on the system PATH
- **AND** the command SHALL execute without import errors

#### Scenario: pipx installation
- **WHEN** a user runs `pipx install .` from the project root
- **THEN** the `memory` command SHALL be available on the system PATH in an isolated environment

### Requirement: ChromaDB runs via Docker Compose
The project SHALL include a `docker-compose.yml` that runs ChromaDB as a server container with persistent storage.

#### Scenario: Starting ChromaDB
- **WHEN** a user runs `docker compose up -d` from the project root
- **THEN** ChromaDB SHALL be accessible at `localhost:8000`
- **AND** data SHALL persist across container restarts via a Docker volume named `chroma_data`
- **AND** ChromaDB telemetry SHALL be disabled via `ANONYMIZED_TELEMETRY=false`

#### Scenario: ChromaDB port configuration
- **WHEN** the `CHROMADB_PORT` environment variable is set
- **THEN** Docker Compose SHALL map that port to ChromaDB's internal port 8000

### Requirement: Project directory structure exists
The project SHALL have a clean layered directory structure supporting CLI, service, and store separation.

#### Scenario: All required directories and init files exist
- **WHEN** the package is installed
- **THEN** the following directories SHALL exist with `__init__.py` files: `src/memories/`, `src/memories/services/`, `src/memories/stores/`
- **AND** the `tests/` directory SHALL exist with a `__init__.py` file

### Requirement: Configuration variables are documented
The project SHALL include a `.env.example` file documenting all supported environment variables with their default values.

#### Scenario: .env.example contains all config vars
- **WHEN** a developer reads `.env.example`
- **THEN** it SHALL document: `CHROMADB_HOST`, `CHROMADB_PORT`, `COLLECTION_NAME`, `DEFAULT_LIMIT`, `MIN_CONFIDENCE`, `DECAY_HALF_LIFE_HOURS`
- **AND** each variable SHALL have a comment explaining its purpose and a default value
