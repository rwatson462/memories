"""Abstract vector store interface.

Defined as a `typing.Protocol` so any class with matching method
signatures satisfies it via structural subtyping — no inheritance
required.
"""

from typing import Protocol


class VectorStore(Protocol):
    """Interface that all vector storage backends must satisfy."""

    def store(self, id: str, content: str, metadata: dict) -> None:
        """Persist a document with its metadata."""
        ...

    def get(self, id: str) -> dict | None:
        """Retrieve a single document by ID, or None if missing."""
        ...

    def search(
        self,
        query: str,
        n_results: int,
        where: dict | None = None,
    ) -> list[dict]:
        """Return documents similar to *query*, optionally filtered."""
        ...

    def delete(self, id: str) -> None:
        """Permanently remove a document by ID."""
        ...

    def update_metadata(self, id: str, metadata: dict) -> None:
        """Merge *metadata* into an existing document's metadata."""
        ...

    def count(self) -> int:
        """Return the total number of stored documents."""
        ...

    def heartbeat(self) -> bool:
        """Return True if the backend is reachable."""
        ...
