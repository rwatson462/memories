"""Unit tests for MemoryService.

All tests use the ``mock_vector_store`` fixture so they run without
ChromaDB.  Each test configures the mock's return values for its
specific scenario.
"""

from datetime import datetime, timezone
from unittest.mock import ANY

import pytest

from memories.models import DecayPolicy, MemoryCreate
from memories.services.memory_service import (
    InvalidOperationError,
    MemoryNotFoundError,
    MemoryService,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_metadata(
    *,
    decay_policy: str = "stable",
    deleted: bool = False,
    created_at: str = "2025-06-01T12:00:00+00:00",
    last_reinforced_at: str = "",
    agent: str = "",
    personality: str = "",
    project: str = "",
    type: str = "",
    global_: bool = False,
) -> dict:
    """Build a metadata dict matching the shape stored by MemoryService."""
    return {
        "agent": agent,
        "personality": personality,
        "project": project,
        "type": type,
        "global_": global_,
        "decay_policy": decay_policy,
        "created_at": created_at,
        "last_reinforced_at": last_reinforced_at,
        "deleted": deleted,
    }


# ---------------------------------------------------------------------------
# create_memory
# ---------------------------------------------------------------------------

class TestCreateMemory:
    """Verify that create_memory stores via the VectorStore and returns correctly."""

    def test_store_called_with_uuid_and_metadata(self, memory_service, mock_vector_store):
        """VectorStore.store is called once with a UUID id and correct metadata."""
        data = MemoryCreate(content="remember this")
        result = memory_service.create_memory(data)

        mock_vector_store.store.assert_called_once()
        call_args = mock_vector_store.store.call_args
        stored_id = call_args[0][0]
        stored_content = call_args[0][1]
        stored_meta = call_args[0][2]

        # ID should be a valid UUID string.
        assert len(stored_id) == 36 and stored_id.count("-") == 4
        assert stored_content == "remember this"
        assert stored_meta["decay_policy"] == "stable"
        assert stored_meta["deleted"] is False

    def test_returns_memory_response_with_confidence_one(self, memory_service):
        """A freshly created memory always has confidence 1.0."""
        data = MemoryCreate(content="test", agent="bot", decay_policy=DecayPolicy.CONTEXTUAL)
        result = memory_service.create_memory(data)

        assert result.confidence == 1.0
        assert result.content == "test"
        assert result.agent == "bot"
        assert result.decay_policy == DecayPolicy.CONTEXTUAL


# ---------------------------------------------------------------------------
# search_memories
# ---------------------------------------------------------------------------

class TestSearchMemories:
    """Verify search filtering, confidence gating, and where-clause construction."""

    def test_confidence_filtering(self, memory_service, mock_vector_store):
        """Results below min_confidence are excluded from the response."""
        now_iso = datetime.now(timezone.utc).isoformat()
        # One fresh result (confidence ~1.0) and one very old (confidence ~0.0).
        mock_vector_store.search.return_value = [
            {
                "id": "fresh",
                "content": "new memory",
                "metadata": _make_metadata(created_at=now_iso, decay_policy="contextual"),
                "distance": 0.1,
            },
            {
                "id": "stale",
                "content": "old memory",
                "metadata": _make_metadata(created_at="2020-01-01T00:00:00+00:00", decay_policy="contextual"),
                "distance": 0.2,
            },
        ]

        result = memory_service.search_memories("query", min_confidence=0.3)

        # Only the fresh result should survive confidence filtering.
        assert result.count == 1
        assert result.results[0].id == "fresh"

    def test_deleted_false_always_in_where(self, memory_service, mock_vector_store):
        """The where filter always includes deleted=False."""
        memory_service.search_memories("query")
        call_args = mock_vector_store.search.call_args
        where = call_args[1].get("where") or call_args[0][2]
        assert where["deleted"] is False

    def test_tag_filters_added(self, memory_service, mock_vector_store):
        """Non-empty tag filters are included in the where clause."""
        memory_service.search_memories("query", agent="bot", project="proj")
        call_args = mock_vector_store.search.call_args
        where = call_args[1].get("where") or call_args[0][2]
        assert where["agent"] == "bot"
        assert where["project"] == "proj"


# ---------------------------------------------------------------------------
# get_memory
# ---------------------------------------------------------------------------

class TestGetMemory:
    """Verify get_memory for found, not-found, and deleted cases."""

    def test_found(self, memory_service, mock_vector_store):
        """Returns a MemoryResponse when the document exists."""
        mock_vector_store.get.return_value = {
            "id": "abc",
            "content": "hello",
            "metadata": _make_metadata(),
        }
        result = memory_service.get_memory("abc")
        assert result.id == "abc"
        assert result.content == "hello"

    def test_not_found_returns_error(self, memory_service, mock_vector_store):
        """Raises MemoryNotFoundError when the store returns None."""
        mock_vector_store.get.return_value = None
        with pytest.raises(MemoryNotFoundError):
            memory_service.get_memory("nonexistent")

    def test_deleted_raises_not_found(self, memory_service, mock_vector_store):
        """A soft-deleted document is treated as not found."""
        mock_vector_store.get.return_value = {
            "id": "del",
            "content": "gone",
            "metadata": _make_metadata(deleted=True),
        }
        with pytest.raises(MemoryNotFoundError):
            memory_service.get_memory("del")


# ---------------------------------------------------------------------------
# reinforce_memory
# ---------------------------------------------------------------------------

class TestReinforceMemory:
    """Verify reinforce logic and policy validation."""

    def test_valid_reinforceable(self, memory_service, mock_vector_store):
        """Reinforcing a reinforceable memory updates last_reinforced_at."""
        mock_vector_store.get.return_value = {
            "id": "r1",
            "content": "reinforceable",
            "metadata": _make_metadata(decay_policy="reinforceable"),
        }
        result = memory_service.reinforce_memory("r1")
        assert result["confidence"] == 1.0
        mock_vector_store.update_metadata.assert_called_once()

    def test_stable_raises_invalid_operation(self, memory_service, mock_vector_store):
        """Cannot reinforce a stable memory."""
        mock_vector_store.get.return_value = {
            "id": "s1",
            "content": "stable",
            "metadata": _make_metadata(decay_policy="stable"),
        }
        with pytest.raises(InvalidOperationError):
            memory_service.reinforce_memory("s1")

    def test_contextual_raises_invalid_operation(self, memory_service, mock_vector_store):
        """Cannot reinforce a contextual memory."""
        mock_vector_store.get.return_value = {
            "id": "c1",
            "content": "contextual",
            "metadata": _make_metadata(decay_policy="contextual"),
        }
        with pytest.raises(InvalidOperationError):
            memory_service.reinforce_memory("c1")

    def test_not_found(self, memory_service, mock_vector_store):
        """Reinforcing a non-existent memory raises MemoryNotFoundError."""
        mock_vector_store.get.return_value = None
        with pytest.raises(MemoryNotFoundError):
            memory_service.reinforce_memory("missing")


# ---------------------------------------------------------------------------
# delete_memory
# ---------------------------------------------------------------------------

class TestDeleteMemory:
    """Verify soft-delete logic."""

    def test_success(self, memory_service, mock_vector_store):
        """Deleting an existing memory sets deleted=True."""
        mock_vector_store.get.return_value = {
            "id": "d1",
            "content": "to delete",
            "metadata": _make_metadata(),
        }
        result = memory_service.delete_memory("d1")
        assert result["deleted"] is True
        mock_vector_store.update_metadata.assert_called_once_with("d1", {"deleted": True})

    def test_already_deleted(self, memory_service, mock_vector_store):
        """Deleting an already-deleted memory raises InvalidOperationError."""
        mock_vector_store.get.return_value = {
            "id": "d2",
            "content": "already gone",
            "metadata": _make_metadata(deleted=True),
        }
        with pytest.raises(InvalidOperationError):
            memory_service.delete_memory("d2")

    def test_not_found(self, memory_service, mock_vector_store):
        """Deleting a non-existent memory raises MemoryNotFoundError."""
        mock_vector_store.get.return_value = None
        with pytest.raises(MemoryNotFoundError):
            memory_service.delete_memory("nonexistent")


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------

class TestGetStatus:
    """Verify health-check status reporting."""

    def test_healthy(self, memory_service, mock_vector_store):
        """When heartbeat succeeds, status is healthy with a count."""
        mock_vector_store.heartbeat.return_value = True
        mock_vector_store.count.return_value = 42
        result = memory_service.get_status()
        assert result["status"] == "healthy"
        assert result["count"] == 42

    def test_unhealthy(self, memory_service, mock_vector_store):
        """When heartbeat fails, status is unhealthy with count 0."""
        mock_vector_store.heartbeat.return_value = False
        result = memory_service.get_status()
        assert result["status"] == "unhealthy"
        assert result["count"] == 0
