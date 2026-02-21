## ADDED Requirements

### Requirement: DecayPolicy enum defines valid policies
The system SHALL define a DecayPolicy enum with exactly three values: stable, contextual, reinforceable.

#### Scenario: Valid decay policy
- **WHEN** a memory is created with decay_policy "stable", "contextual", or "reinforceable"
- **THEN** the value SHALL be accepted

#### Scenario: Invalid decay policy
- **WHEN** a memory is created with an unrecognized decay_policy value
- **THEN** the system SHALL reject it with a validation error

### Requirement: MemoryCreate model validates input
The system SHALL define a MemoryCreate model with: content (str, required), agent (str, optional), personality (str, optional), project (str, optional), type (str, optional), global_ (bool, default false), decay_policy (DecayPolicy, default stable).

#### Scenario: Minimal valid memory
- **WHEN** a MemoryCreate is constructed with only content="test"
- **THEN** it SHALL succeed with defaults: agent="", personality="", project="", type="", global_=false, decay_policy=stable

#### Scenario: Full memory
- **WHEN** a MemoryCreate is constructed with all fields populated
- **THEN** all field values SHALL be preserved exactly as provided

### Requirement: MemoryResponse model includes computed fields
The system SHALL define a MemoryResponse model with all stored fields plus confidence (float) and optionally similarity (float, for search results).

#### Scenario: Response includes confidence
- **WHEN** a memory is returned to the caller
- **THEN** the response SHALL include an `id`, `content`, all metadata fields, `confidence` (float 0.0-1.0), and `created_at` (ISO 8601 string)

### Requirement: SearchResponse wraps results with count
The system SHALL define a SearchResponse model with results (list of MemoryResponse) and count (int).

#### Scenario: Search response structure
- **WHEN** a search returns 3 memories
- **THEN** the SearchResponse SHALL have results with 3 items and count=3
