## Context

The CLI layer is the user-facing surface of the memory system. It translates shell commands into MemoryService calls and formats the results. It must be thin — all business logic lives in the service layer (M3).

## Goals / Non-Goals

**Goals:**
- All 6 commands fully functional with proper argument parsing
- JSON default output, text optional
- Consistent error handling across all commands
- Clean dependency wiring: config → adapter → service

**Non-Goals:**
- Shell completion (can be added later with Typer's built-in support)
- Interactive prompts (agents can't interact)
- Colored output (agents parse stdout; colors would interfere)

## Decisions

### Typer app structure: single file with callbacks
All 6 commands in a single `cli.py` file. At this scale, splitting into multiple files adds complexity without benefit. Each command is a decorated function calling the corresponding MemoryService method.

**Global options:** The `--format` flag is defined as a Typer callback or repeated on each command. Since Typer doesn't natively support global options elegantly, define it as a parameter on each command function for clarity.

### Dependency wiring: module-level setup in __init__.py
`__init__.py` instantiates: Settings → ChromaDBAdapter(settings) → MemoryService(adapter, settings). The Typer app in `cli.py` imports the service instance from the package. This is simple and appropriate for a CLI tool (no dependency injection framework needed).

**Error resilience:** The adapter connection is lazy — ChromaDB is only contacted when a command actually executes, not on import. This means `memory --help` works even if ChromaDB is down.

### Output formatting: helper functions
Two helper functions: `output_json(data, file=stdout)` and `output_text(data, file=stdout)`. Each command calls the appropriate one based on the --format flag. JSON uses `json.dumps` with `indent=2` for readability. Text uses simple key-value formatting.

### Error handling: try/except at command level
Each command wraps its service call in a try/except that catches:
- `MemoryNotFoundError` → `{"error": "Memory not found"}` to stderr, exit 1
- `InvalidOperationError` → `{"error": message}` to stderr, exit 1
- `Exception` (ChromaDB connection errors, etc.) → `{"error": "Cannot connect to ChromaDB..."}` to stderr, exit 1

Use `raise typer.Exit(code=1)` after writing to stderr.

## Risks / Trade-offs

- [Risk] Module-level service instantiation means import errors crash all commands → Mitigated by making adapter connection lazy (no ChromaDB call until a command runs).
- [Trade-off] Repeating --format on every command vs Typer callback → Repeating is more explicit and avoids Typer callback complexity. Acceptable for 6 commands.
