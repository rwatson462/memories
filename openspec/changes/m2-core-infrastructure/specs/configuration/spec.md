## ADDED Requirements

### Requirement: Configuration loads from environment variables
The system SHALL load all configuration from environment variables, with sensible defaults for local development.

#### Scenario: Default configuration
- **WHEN** no environment variables are set
- **THEN** the configuration SHALL use these defaults: CHROMADB_HOST=localhost, CHROMADB_PORT=8000, COLLECTION_NAME=memories, DEFAULT_LIMIT=10, MIN_CONFIDENCE=0.3, DECAY_HALF_LIFE_HOURS=720

#### Scenario: Environment variable override
- **WHEN** an environment variable like `CHROMADB_HOST=chromadb-server` is set
- **THEN** the configuration SHALL use the overridden value instead of the default

#### Scenario: .env file support
- **WHEN** a `.env` file exists in the project root
- **THEN** pydantic-settings SHALL read values from it as a fallback behind actual environment variables
