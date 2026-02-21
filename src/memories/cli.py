"""CLI commands for the memory system.

Thin layer that translates shell arguments into MemoryService calls
and formats the results.  All business logic lives in the service layer.
"""

import json
import sys

import typer

from memories.config import settings
from memories.models import DecayPolicy, MemoryCreate, OutputFormat
from memories.services.memory_service import InvalidOperationError, MemoryNotFoundError

app = typer.Typer()


# Force Typer to keep subcommand mode even with a single command.
@app.callback()
def main() -> None:
    """Persistent, searchable memory for AI agents."""


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def output_json(data: dict, file=None) -> None:
    """Serialize *data* as pretty-printed JSON.

    Resolves *file* at call time (not import time) so that
    typer.testing.CliRunner's stdout redirection works correctly.
    """
    file = file or sys.stdout
    print(json.dumps(data, indent=2, default=str), file=file)


def output_text(data: dict, file=None) -> None:
    """Render *data* as human-readable text.

    Single-memory output uses padded key-value alignment.
    Search output prints each result separated by blank lines
    with a summary count at the end.
    """
    file = file or sys.stdout

    # Search results get special treatment: per-result blocks + summary.
    if "results" in data and isinstance(data["results"], list):
        for i, item in enumerate(data["results"]):
            if isinstance(item, dict):
                _print_padded(item, file)
            if i < len(data["results"]) - 1:
                print(file=file)  # Blank line between results.
        count = data.get("count", len(data["results"]))
        print(f"\nFound {count} memories", file=file)
        return

    # Single-memory or status output: padded key-value pairs.
    _print_padded(data, file)


def _print_padded(data: dict, file) -> None:
    """Print a dict as padded ``Key:  value`` lines for readability."""
    if not data:
        return
    # Pad all keys to the width of the longest key.
    max_key = max(len(str(k)) for k in data)
    for key, value in data.items():
        label = f"{key}:".ljust(max_key + 2)
        print(f"{label}{value}", file=file)


def _output(data: dict, fmt: OutputFormat, file=None) -> None:
    """Route to the appropriate formatter based on ``--format``."""
    file = file or sys.stdout
    if fmt == OutputFormat.JSON:
        output_json(data, file=file)
    else:
        output_text(data, file=file)


def _clean_output(data: dict) -> dict:
    """Rename internal field names to their user-facing equivalents.

    Pydantic models use ``global_`` to avoid shadowing the Python
    keyword; the CLI output uses ``global``.
    """
    if "global_" in data:
        data["global"] = data.pop("global_")
    if "results" in data:
        for item in data["results"]:
            if "global_" in item:
                item["global"] = item.pop("global_")
    return data


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def _handle_error(exc: Exception) -> None:
    """Write a JSON error object to stderr and exit with code 1.

    Distinguishes service-level exceptions (not-found, invalid-op)
    from unexpected errors (assumed to be ChromaDB connection failures).
    """
    if isinstance(exc, MemoryNotFoundError):
        output_json({"error": f"Memory '{exc.id}' not found"}, file=sys.stderr)
    elif isinstance(exc, InvalidOperationError):
        output_json({"error": str(exc)}, file=sys.stderr)
    else:
        host = f"{settings.chromadb_host}:{settings.chromadb_port}"
        output_json(
            {"error": f"Cannot connect to ChromaDB at {host}. Is Docker running?"},
            file=sys.stderr,
        )
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Lazy service access
# ---------------------------------------------------------------------------


def _get_service():
    """Return the lazily-initialized MemoryService."""
    from memories import get_service

    return get_service()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def create(
    content: str = typer.Argument(..., help="Memory content to store"),
    agent: str = typer.Option("", help="Agent identifier"),
    personality: str = typer.Option("", help="Personality identifier"),
    project: str = typer.Option("", help="Project identifier"),
    type: str = typer.Option("", help="Memory type"),
    global_: bool = typer.Option(False, "--global", help="Mark as global memory"),
    decay: DecayPolicy = typer.Option(DecayPolicy.STABLE, help="Decay policy"),
    format: OutputFormat = typer.Option(OutputFormat.JSON, help="Output format"),
) -> None:
    """Store a new memory."""
    try:
        service = _get_service()
        data = MemoryCreate(
            content=content,
            agent=agent,
            personality=personality,
            project=project,
            type=type,
            global_=global_,
            decay_policy=decay,
        )
        result = service.create_memory(data)
        _output(_clean_output(result.model_dump(mode="json")), format)
    except typer.Exit:
        raise
    except Exception as exc:
        _handle_error(exc)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    agent: str = typer.Option("", help="Filter by agent"),
    personality: str = typer.Option("", help="Filter by personality"),
    project: str = typer.Option("", help="Filter by project"),
    type: str = typer.Option("", help="Filter by memory type"),
    global_: bool = typer.Option(False, "--global", help="Filter to global memories"),
    limit: int = typer.Option(10, help="Max results to return"),
    min_confidence: float = typer.Option(
        0.3, "--min-confidence", help="Minimum confidence threshold"
    ),
    format: OutputFormat = typer.Option(OutputFormat.JSON, help="Output format"),
) -> None:
    """Search memories by semantic similarity."""
    try:
        service = _get_service()
        result = service.search_memories(
            query=query,
            agent=agent,
            personality=personality,
            project=project,
            type_=type,
            # --global flag means "only global"; absence means "no filter".
            global_=True if global_ else None,
            limit=limit,
            min_confidence=min_confidence,
        )
        _output(_clean_output(result.model_dump(mode="json")), format)
    except typer.Exit:
        raise
    except Exception as exc:
        _handle_error(exc)


@app.command()
def get(
    id: str = typer.Argument(..., help="Memory ID"),
    format: OutputFormat = typer.Option(OutputFormat.JSON, help="Output format"),
) -> None:
    """Retrieve a memory by ID."""
    try:
        service = _get_service()
        result = service.get_memory(id)
        _output(_clean_output(result.model_dump(mode="json")), format)
    except typer.Exit:
        raise
    except Exception as exc:
        _handle_error(exc)


@app.command()
def reinforce(
    id: str = typer.Argument(..., help="Memory ID"),
    format: OutputFormat = typer.Option(OutputFormat.JSON, help="Output format"),
) -> None:
    """Reinforce a memory (reset its decay timer)."""
    try:
        service = _get_service()
        result = service.reinforce_memory(id)
        # Map service field name to spec-expected name.
        output_data = {
            "id": result["id"],
            "confidence": result["confidence"],
            "last_reinforced_at": result["reinforced_at"],
        }
        _output(output_data, format)
    except typer.Exit:
        raise
    except Exception as exc:
        _handle_error(exc)


@app.command()
def delete(
    id: str = typer.Argument(..., help="Memory ID"),
    format: OutputFormat = typer.Option(OutputFormat.JSON, help="Output format"),
) -> None:
    """Soft-delete a memory."""
    try:
        service = _get_service()
        result = service.delete_memory(id)
        _output(result, format)
    except typer.Exit:
        raise
    except Exception as exc:
        _handle_error(exc)


@app.command()
def status(
    format: OutputFormat = typer.Option(OutputFormat.JSON, help="Output format"),
) -> None:
    """Check ChromaDB connection health and report status."""
    try:
        service = _get_service()
        result = service.get_status()
        if result["status"] == "unhealthy":
            # Unhealthy status goes to stderr with exit code 1.
            output_json(result, file=sys.stderr)
            raise typer.Exit(code=1)
        _output(result, format)
    except typer.Exit:
        raise
    except Exception:
        # Can't even connect — report unhealthy with connection details.
        host = f"{settings.chromadb_host}:{settings.chromadb_port}"
        output_json(
            {
                "status": "unhealthy",
                "host": host,
                "error": f"Cannot connect to ChromaDB at {host}. Is Docker running?",
            },
            file=sys.stderr,
        )
        raise typer.Exit(code=1)
