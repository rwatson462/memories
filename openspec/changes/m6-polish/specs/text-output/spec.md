## ADDED Requirements

### Requirement: Text format provides readable key-value output
When `--format text` is used, output SHALL be human-readable key-value pairs, not JSON.

#### Scenario: Text output for memory create
- **WHEN** `memory create "test" --format text` is executed
- **THEN** stdout SHALL display fields in a readable format, for example:
  ```
  ID:          a1b2c3d4-...
  Content:     test
  Agent:
  Decay:       stable
  Confidence:  1.0
  Created:     2026-02-21T10:00:00Z
  ```

#### Scenario: Text output for search results
- **WHEN** `memory search "test" --format text` is executed
- **THEN** stdout SHALL display each result separated by a blank line with key-value formatting
- **AND** a summary line SHALL show the total count (e.g., "Found 3 memories")

### Requirement: Text format is human-oriented, not machine-parseable
The text format is for human debugging only. Agents SHALL use the default JSON format.

#### Scenario: Text output is not valid JSON
- **WHEN** any command is executed with `--format text`
- **THEN** stdout SHALL NOT be valid JSON
