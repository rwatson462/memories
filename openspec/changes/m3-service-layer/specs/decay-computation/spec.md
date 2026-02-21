## ADDED Requirements

### Requirement: Stable decay policy never loses confidence
Memories with the "stable" decay policy SHALL always have a confidence of 1.0 regardless of age.

#### Scenario: Stable memory after 1 year
- **WHEN** a memory with decay_policy="stable" was created 365 days ago
- **THEN** its computed confidence SHALL be 1.0

### Requirement: Contextual decay policy loses confidence linearly
Memories with the "contextual" decay policy SHALL lose confidence linearly from 1.0 to 0.0 over the configured half-life period.

#### Scenario: Contextual memory at creation
- **WHEN** a memory with decay_policy="contextual" was just created (age=0)
- **THEN** its computed confidence SHALL be 1.0

#### Scenario: Contextual memory at half of half-life
- **WHEN** a memory with decay_policy="contextual" is 360 hours old (half of default 720-hour half-life)
- **THEN** its computed confidence SHALL be 0.5

#### Scenario: Contextual memory at full half-life
- **WHEN** a memory with decay_policy="contextual" is 720 hours old (equal to half-life)
- **THEN** its computed confidence SHALL be 0.0

#### Scenario: Contextual memory beyond half-life
- **WHEN** a memory with decay_policy="contextual" is older than the half-life
- **THEN** its computed confidence SHALL be 0.0 (never negative)

### Requirement: Reinforceable decay policy resets on reinforcement
Memories with the "reinforceable" decay policy SHALL decay like contextual, but age is measured from the last reinforcement time instead of creation time.

#### Scenario: Reinforceable memory never reinforced
- **WHEN** a memory with decay_policy="reinforceable" has never been reinforced
- **THEN** decay SHALL be calculated from created_at (same as contextual)

#### Scenario: Reinforceable memory after reinforcement
- **WHEN** a memory with decay_policy="reinforceable" was created 600 hours ago
- **AND** it was reinforced 10 hours ago
- **THEN** decay SHALL be calculated from the reinforcement time
- **AND** its computed confidence SHALL be approximately 0.986 (1.0 - 10/720)

### Requirement: Confidence is rounded to 4 decimal places
All computed confidence values SHALL be rounded to 4 decimal places.

#### Scenario: Rounding precision
- **WHEN** confidence is computed as 0.86111111
- **THEN** the returned value SHALL be 0.8611
