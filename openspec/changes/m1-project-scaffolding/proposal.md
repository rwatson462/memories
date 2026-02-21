## Why

The Memories project needs a properly structured Python package foundation before any feature code can be written. This milestone creates the installable package skeleton, Docker Compose configuration for ChromaDB, and the directory structure that all subsequent milestones build on.

## What Changes

- New Python package `memories` with `pyproject.toml` and entry point registration
- Docker Compose file to run ChromaDB as a separate container with persistent volume
- Project directory structure: `src/memories/`, `src/memories/services/`, `src/memories/stores/`, `tests/`
- `.env.example` documenting all configuration variables
- Package installable via `pip install -e .` with `memory` command registered

## Capabilities

### New Capabilities
- `project-setup`: Installable Python package with Docker Compose infrastructure

### Modified Capabilities
(none)

## Impact

- Creates all foundational files: `pyproject.toml`, `docker-compose.yml`, `.env.example`, directory structure with `__init__.py` files
- Establishes the `memory` CLI entry point (placeholder — real commands come in M4)
- ChromaDB Docker container provides the persistence layer for all subsequent milestones
