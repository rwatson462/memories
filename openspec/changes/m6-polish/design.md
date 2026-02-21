## Context

This is a polish milestone — no new architecture, just refinements to error handling, output formatting, and security. All changes are within existing files.

## Goals / Non-Goals

**Goals:**
- Every error message helps the user fix the problem
- Text output is clean and scannable for human debugging
- ChromaDB is not accidentally exposed to the network

**Non-Goals:**
- Changing any business logic or data model
- Adding new commands or features
- Comprehensive security audit (trusted network model still applies)

## Decisions

### Error message format: include context and guidance
Every error message includes: what went wrong, what was being attempted, and how to fix it. For ChromaDB errors, always include the host:port and suggest "Is Docker running?"

### Text formatter: simple key-value layout
Use a basic approach: for single-memory output, print `Key:  value` pairs (padded for alignment). For search results, print each memory separated by a blank line, with a summary line at the end. Keep it simple — this is a debugging aid, not a rich TUI.

**Alternative considered:** Rich library for tables and colors. Overkill for a tool primarily used by AI agents. Plain text is more portable.

### Localhost binding: 127.0.0.1 prefix
Change the Docker Compose port mapping from `${CHROMADB_PORT:-8000}:8000` to `127.0.0.1:${CHROMADB_PORT:-8000}:8000`. This is a single-character-level change with meaningful security benefit.

## Risks / Trade-offs

- [Risk] Localhost binding breaks remote access if someone wants to run ChromaDB on a different machine → This is explicitly a non-goal (single-user, single-machine). If needed later, the user can modify docker-compose.yml.
