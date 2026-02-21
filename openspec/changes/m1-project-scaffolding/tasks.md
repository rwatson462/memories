## 1. Package Configuration

- [x] 1.1 Create `pyproject.toml` with project metadata (name: memories, version: 0.1.0, python: >=3.11), dependencies (typer>=0.9, chromadb>=0.4, pydantic>=2.0, pydantic-settings>=2.0), dev dependencies (pytest, httpx), and `[project.scripts]` entry point: `memory = "memories.cli:app"`
- [x] 1.2 Create `.env.example` with all configuration variables: CHROMADB_HOST=localhost, CHROMADB_PORT=8000, COLLECTION_NAME=memories, DEFAULT_LIMIT=10, MIN_CONFIDENCE=0.3, DECAY_HALF_LIFE_HOURS=720 — each with a descriptive comment

## 2. Directory Structure

- [x] 2.1 Create `src/memories/__init__.py` (empty or minimal package marker)
- [x] 2.2 Create `src/memories/services/__init__.py` (empty)
- [x] 2.3 Create `src/memories/stores/__init__.py` (empty)
- [x] 2.4 Create `tests/__init__.py` (empty)
- [x] 2.5 Create placeholder `src/memories/cli.py` with a minimal Typer app (single `memory status` command that prints "not implemented") so the entry point resolves on install

## 3. Docker Infrastructure

- [x] 3.1 Create `docker-compose.yml` with ChromaDB service: image `chromadb/chroma:latest`, port mapping `${CHROMADB_PORT:-8000}:8000`, volume `chroma_data:/chroma/chroma`, environment `ANONYMIZED_TELEMETRY=false`

## 4. Verification

- [x] 4.1 Verify `docker compose up -d` starts ChromaDB and it responds at localhost:8000 *(requires Docker running)*
- [x] 4.2 Verify `pip install -e .` succeeds and `memory` command is available on PATH
- [x] 4.3 Verify `memory status` runs without import errors (prints placeholder output)
