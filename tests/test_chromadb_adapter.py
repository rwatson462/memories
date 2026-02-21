"""Integration tests for ChromaDBAdapter.

These tests require a running ChromaDB instance (``docker compose up``).
Each test gets a unique collection via the ``chromadb_adapter`` fixture
to prevent cross-test contamination.
"""

import pytest

pytestmark = pytest.mark.integration


class TestStoreAndGet:
    """Verify round-trip persistence of documents."""

    def test_store_get_round_trip(self, chromadb_adapter):
        """A stored document can be retrieved with matching content and metadata."""
        meta = {"agent": "bot", "type": "fact"}
        chromadb_adapter.store("id-1", "the sky is blue", meta)

        result = chromadb_adapter.get("id-1")
        assert result is not None
        assert result["id"] == "id-1"
        assert result["content"] == "the sky is blue"
        assert result["metadata"]["agent"] == "bot"
        assert result["metadata"]["type"] == "fact"

    def test_get_missing_returns_none(self, chromadb_adapter):
        """Getting a non-existent ID returns None."""
        assert chromadb_adapter.get("no-such-id") is None


class TestSearch:
    """Verify semantic search and metadata filtering."""

    def test_search_returns_results_by_relevance(self, chromadb_adapter):
        """Searching returns results ordered by relevance to the query."""
        chromadb_adapter.store("s1", "Python is a programming language", {"tag": "a"})
        chromadb_adapter.store("s2", "The weather is nice today", {"tag": "a"})
        chromadb_adapter.store("s3", "JavaScript runs in the browser", {"tag": "a"})

        results = chromadb_adapter.search("programming languages", n_results=3)
        assert len(results) == 3
        # The programming-related docs should rank higher than weather.
        ids = [r["id"] for r in results]
        assert ids[0] in ("s1", "s3")  # Either programming doc should be first.

    def test_search_with_where_filter(self, chromadb_adapter):
        """Only documents matching the where filter are returned."""
        chromadb_adapter.store("f1", "apples are fruits", {"category": "food"})
        chromadb_adapter.store("f2", "cars are vehicles", {"category": "transport"})

        results = chromadb_adapter.search(
            "fruits", n_results=10, where={"category": "food"},
        )
        assert len(results) == 1
        assert results[0]["id"] == "f1"

    def test_search_with_compound_and_filter(self, chromadb_adapter):
        """Multiple where conditions are combined with $and."""
        chromadb_adapter.store("c1", "doc one", {"agent": "a", "project": "x"})
        chromadb_adapter.store("c2", "doc two", {"agent": "a", "project": "y"})
        chromadb_adapter.store("c3", "doc three", {"agent": "b", "project": "x"})

        results = chromadb_adapter.search(
            "doc", n_results=10, where={"agent": "a", "project": "x"},
        )
        assert len(results) == 1
        assert results[0]["id"] == "c1"


class TestUpdateMetadata:
    """Verify metadata updates are partial (merge, not replace)."""

    def test_update_single_key(self, chromadb_adapter):
        """Updating one metadata key does not affect other keys."""
        chromadb_adapter.store("u1", "update test", {"key_a": "original", "key_b": "keep"})
        chromadb_adapter.update_metadata("u1", {"key_a": "changed"})

        result = chromadb_adapter.get("u1")
        assert result["metadata"]["key_a"] == "changed"
        assert result["metadata"]["key_b"] == "keep"


class TestDelete:
    """Verify permanent document deletion."""

    def test_delete_makes_get_return_none(self, chromadb_adapter):
        """After deletion, get returns None for that ID."""
        chromadb_adapter.store("d1", "to be deleted", {"a": "b"})
        chromadb_adapter.delete("d1")
        assert chromadb_adapter.get("d1") is None


class TestHeartbeat:
    """Verify connectivity check."""

    def test_heartbeat_returns_true(self, chromadb_adapter):
        """A running ChromaDB instance responds to heartbeat."""
        assert chromadb_adapter.heartbeat() is True


class TestCount:
    """Verify document counting."""

    def test_count_matches_stored_documents(self, chromadb_adapter):
        """Count reflects the number of stored documents."""
        assert chromadb_adapter.count() == 0
        chromadb_adapter.store("n1", "first", {"x": "1"})
        chromadb_adapter.store("n2", "second", {"x": "2"})
        chromadb_adapter.store("n3", "third", {"x": "3"})
        assert chromadb_adapter.count() == 3
