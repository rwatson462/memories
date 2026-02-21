## Context

This is the foundation milestone for the Memories CLI tool. No code exists yet. We need a standard Python package structure that supports:
- CLI entry point via Typer (installed in M4)
- Layered architecture: CLI → Service → Store
- Docker-managed ChromaDB for vector storage
- Environment-based configuration

## Goals / Non-Goals

**Goals:**
- Installable Python package with `memory` console script entry point
- ChromaDB running reliably via Docker Compose with persistent storage
- Clean directory structure that enforces architectural layer separation
- All configuration variables documented with sensible defaults

**Non-Goals:**
- No feature code — just the skeleton
- No tests yet (M5)
- No CI/CD pipeline

## Decisions

### Python package layout: src layout
Use `src/memories/` (src layout) rather than flat `memories/` layout. The src layout prevents accidental imports of the local package during development and is the recommended approach for modern Python packages per PyPA guidelines.

**Alternative considered:** Flat layout (`memories/` at root). Simpler but can cause import ambiguity.

### Entry point registration: pyproject.toml `[project.scripts]`
Register the `memory` command via `[project.scripts]` in `pyproject.toml`: `memory = "memories.cli:app"`. This is the standard modern approach (PEP 621).

**Alternative considered:** `setup.py` with `console_scripts`. Legacy approach — `pyproject.toml` is preferred.

### Docker Compose: ChromaDB only
Docker Compose runs only ChromaDB. The CLI runs on the host. This keeps the feedback loop fast (no container rebuild for CLI changes) and matches the pipx distribution model.

### ChromaDB port binding
Default to `localhost:8000` but make the port configurable via `CHROMADB_PORT` env var in Docker Compose using variable substitution (`${CHROMADB_PORT:-8000}`).

## Risks / Trade-offs

- [Risk] ChromaDB Docker image version may introduce breaking changes → Pin to a specific version tag rather than `latest` once stabilized. Use `latest` for now during initial development.
- [Risk] src layout adds a layer of directory nesting → Acceptable tradeoff for import safety. Standard practice.
