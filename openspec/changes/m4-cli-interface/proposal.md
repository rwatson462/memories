## Why

With the service layer complete (M3), we need to wire up the user-facing CLI commands. The CLI is the sole interface to the memory system — every AI agent and human interacts through it. This milestone replaces the placeholder Typer app (from M1) with fully functional commands that invoke the MemoryService and format output as JSON or text.

## What Changes

- Replace placeholder `cli.py` with full Typer app defining all 6 commands
- Wire each command to corresponding MemoryService methods
- Implement JSON (default) and text output formatting
- Implement error handling: catch service exceptions, output JSON to stderr, exit code 1
- Set up package-level initialization (__init__.py) to wire config → adapter → service → CLI

## Capabilities

### New Capabilities
- `cli-commands`: All 6 CLI commands (create, search, get, reinforce, delete, status) with argument parsing and output formatting

### Modified Capabilities
(none)

## Impact

- Rewrites `src/memories/cli.py` (replaces M1 placeholder)
- Creates/updates `src/memories/__init__.py` for dependency wiring
- This is the user-facing surface — all CLI commands become functional after this milestone
- Depends on: MemoryService (M3), Models (M2), Config (M2), ChromaDBAdapter (M2)
