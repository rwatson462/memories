"""Shared fixtures for the memories test suite.

Provides both isolated (mocked) and integration (real ChromaDB) fixtures.
Integration fixtures require a running ChromaDB instance; tests that use
them are marked with ``@pytest.mark.integration``.
"""

import uuid
from unittest.mock import MagicMock

import pytest

from memories.config import Settings
from memories.services.memory_service import MemoryService
from memories.stores.chromadb_adapter import ChromaDBAdapter


# ---------------------------------------------------------------------------
# Pytest marker registration
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Register custom markers so pytest doesn't warn about them."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require a running ChromaDB instance",
    )


# ---------------------------------------------------------------------------
# Settings fixture — uses a unique collection name per test
# ---------------------------------------------------------------------------

@pytest.fixture()
def settings():
    """Return a Settings instance with a unique collection name."""
    return Settings(
        chromadb_host="localhost",
        chromadb_port=8000,
        collection_name=f"test_{uuid.uuid4().hex[:12]}",
    )


# ---------------------------------------------------------------------------
# Mock vector store — unit-test friendly, no network
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_vector_store():
    """Return a MagicMock satisfying the VectorStore Protocol."""
    mock = MagicMock()
    mock.store.return_value = None
    mock.get.return_value = None
    mock.search.return_value = []
    mock.delete.return_value = None
    mock.update_metadata.return_value = None
    mock.count.return_value = 0
    mock.heartbeat.return_value = True
    return mock


# ---------------------------------------------------------------------------
# Service with mocked store — for unit tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def memory_service(mock_vector_store, settings):
    """Return a MemoryService wired to the mock vector store."""
    return MemoryService(store=mock_vector_store, settings=settings)


# ---------------------------------------------------------------------------
# Real ChromaDB adapter — for integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def chromadb_adapter(settings):
    """Create a real ChromaDBAdapter with a disposable test collection.

    Tears down the collection after the test to avoid cross-test
    contamination.
    """
    adapter = ChromaDBAdapter(
        host=settings.chromadb_host,
        port=settings.chromadb_port,
        collection_name=settings.collection_name,
    )
    yield adapter
    # Cleanup: delete the test collection.
    try:
        adapter._client.delete_collection(settings.collection_name)
    except Exception:
        pass  # Best-effort cleanup; don't fail the test.


# ---------------------------------------------------------------------------
# Service with real ChromaDB — for integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def real_memory_service(chromadb_adapter, settings):
    """Return a MemoryService wired to a real ChromaDB adapter."""
    return MemoryService(store=chromadb_adapter, settings=settings)
