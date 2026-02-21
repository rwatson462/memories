"""Minimal Typer app — placeholder for the memory CLI entry point.

Real commands are added in M4. This file exists so that `pip install -e .`
registers the `memory` console script without import errors.
"""

import typer

app = typer.Typer()


# Force Typer to keep subcommand mode even with a single command.
@app.callback()
def main() -> None:
    """Persistent, searchable memory for AI agents."""


@app.command()
def status() -> None:
    """Check ChromaDB connection health and report status."""
    typer.echo("not implemented")
