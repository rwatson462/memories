"""Memories package — persistent, searchable memory for AI agents.

Wires configuration → adapter → service.  The adapter and service are
instantiated lazily so that import-time operations (``--help``, tab
completion) work even when ChromaDB is unreachable.
"""

from memories.config import settings


def get_service():
    """Return the lazily-initialized MemoryService singleton.

    Defers ChromaDB connection until a command actually runs, so
    ``memory --help`` works without a running database.
    """
    if not hasattr(get_service, "_instance"):
        from memories.services.memory_service import MemoryService
        from memories.stores.chromadb_adapter import ChromaDBAdapter

        adapter = ChromaDBAdapter(
            host=settings.chromadb_host,
            port=settings.chromadb_port,
            collection_name=settings.collection_name,
        )
        get_service._instance = MemoryService(store=adapter, settings=settings)
    return get_service._instance
