"""End-to-end CLI tests via typer.testing.CliRunner.

These tests invoke the actual CLI commands in-process and validate
JSON output and exit codes.  Requires a running ChromaDB instance.
"""

import json
import uuid

import pytest
from typer.testing import CliRunner

from memories.cli import app

pytestmark = pytest.mark.integration

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unique_content():
    """Generate unique content to avoid collisions across test runs."""
    return f"test-memory-{uuid.uuid4().hex[:8]}"


def _create_memory(content: str = "", **kwargs) -> dict:
    """Create a memory via CLI and return parsed JSON output."""
    content = content or _unique_content()
    args = ["create", content]
    for key, value in kwargs.items():
        if key == "global_":
            if value:
                args.append("--global")
        else:
            args.extend([f"--{key}", str(value)])
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"Create failed: {result.output}"
    return json.loads(result.output)


# ---------------------------------------------------------------------------
# create command
# ---------------------------------------------------------------------------

class TestCreateCommand:
    """Verify the create command output and field presence."""

    def test_create_returns_all_fields(self):
        """Created memory JSON contains all expected fields."""
        output = _create_memory("hello world")
        expected_fields = {
            "id", "content", "agent", "personality", "project",
            "type", "global", "decay_policy", "confidence", "created_at",
        }
        assert expected_fields.issubset(output.keys())
        assert output["content"] == "hello world"
        assert output["confidence"] == 1.0


# ---------------------------------------------------------------------------
# search command
# ---------------------------------------------------------------------------

class TestSearchCommand:
    """Verify search finds previously created memories."""

    def test_search_finds_created_memory(self):
        """A just-created memory appears in search results."""
        content = _unique_content()
        created = _create_memory(content)

        result = runner.invoke(app, ["search", content])
        assert result.exit_code == 0
        output = json.loads(result.output)
        result_ids = [r["id"] for r in output["results"]]
        assert created["id"] in result_ids


# ---------------------------------------------------------------------------
# get command
# ---------------------------------------------------------------------------

class TestGetCommand:
    """Verify get by ID works correctly."""

    def test_get_returns_memory(self):
        """Getting a memory by ID returns the correct content."""
        created = _create_memory("get test")
        result = runner.invoke(app, ["get", created["id"]])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["id"] == created["id"]
        assert output["content"] == "get test"

    def test_get_nonexistent_exits_with_error(self):
        """Getting a non-existent ID exits with code 1 and error JSON."""
        result = runner.invoke(app, ["get", "nonexistent-id-12345"])
        assert result.exit_code == 1
        # Error goes to stderr; CliRunner merges streams by default.
        # Check that "error" appears somewhere in the combined output.
        assert "error" in result.output.lower() or "not found" in result.output.lower()


# ---------------------------------------------------------------------------
# reinforce command
# ---------------------------------------------------------------------------

class TestReinforceCommand:
    """Verify reinforce for valid and invalid cases."""

    def test_reinforce_reinforceable_memory(self):
        """Reinforcing a reinforceable memory returns confidence 1.0."""
        created = _create_memory(decay="reinforceable")
        result = runner.invoke(app, ["reinforce", created["id"]])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["confidence"] == 1.0

    def test_reinforce_stable_memory_fails(self):
        """Reinforcing a stable memory exits with code 1."""
        created = _create_memory(decay="stable")
        result = runner.invoke(app, ["reinforce", created["id"]])
        assert result.exit_code == 1


# ---------------------------------------------------------------------------
# delete command
# ---------------------------------------------------------------------------

class TestDeleteCommand:
    """Verify soft-delete via CLI."""

    def test_delete_returns_confirmation(self):
        """Deleting a memory returns its ID and deleted=True."""
        created = _create_memory("delete me")
        result = runner.invoke(app, ["delete", created["id"]])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["id"] == created["id"]
        assert output["deleted"] is True


# ---------------------------------------------------------------------------
# status command
# ---------------------------------------------------------------------------

class TestStatusCommand:
    """Verify the status health check."""

    def test_status_healthy(self):
        """Status reports healthy when ChromaDB is running."""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["status"] == "healthy"


# ---------------------------------------------------------------------------
# --format text
# ---------------------------------------------------------------------------

class TestTextFormat:
    """Verify that --format text produces non-JSON output."""

    def test_create_text_format(self):
        """Text format output is not valid JSON."""
        result = runner.invoke(app, ["create", "text format test", "--format", "text"])
        assert result.exit_code == 0
        # Text output should not be parseable as JSON.
        with pytest.raises(json.JSONDecodeError):
            json.loads(result.output)
        # But it should contain key-value pairs.
        assert "content:" in result.output or "id:" in result.output
