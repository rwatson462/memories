"""ChromaDB implementation of the VectorStore protocol.

Connects to a ChromaDB server over HTTP and translates the generic
VectorStore interface into ChromaDB collection API calls.
"""

import chromadb


class ChromaDBAdapter:
    """VectorStore backed by a remote ChromaDB instance."""

    def __init__(self, host: str, port: int, collection_name: str) -> None:
        self._client = chromadb.HttpClient(host=host, port=port)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
        )

    # ------------------------------------------------------------------
    # VectorStore protocol methods
    # ------------------------------------------------------------------

    def store(self, id: str, content: str, metadata: dict) -> None:
        """Persist a document.  ChromaDB generates the embedding."""
        self._collection.add(ids=[id], documents=[content], metadatas=[metadata])

    def get(self, id: str) -> dict | None:
        """Retrieve a document by ID, or None if it doesn't exist."""
        result = self._collection.get(ids=[id])
        if not result["ids"]:
            return None
        return {
            "id": result["ids"][0],
            "content": result["documents"][0],
            "metadata": result["metadatas"][0],
        }

    def search(
        self,
        query: str,
        n_results: int,
        where: dict | None = None,
    ) -> list[dict]:
        """Semantic search with optional metadata filtering.

        When *where* has multiple keys, they are combined with ChromaDB's
        ``$and`` operator so every condition must match.
        """
        kwargs: dict = {"query_texts": [query], "n_results": n_results}
        if where:
            kwargs["where"] = _build_where(where)

        result = self._collection.query(**kwargs)

        # query() returns lists-of-lists; we always pass a single query.
        ids = result["ids"][0]
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        distances = result["distances"][0]

        return [
            {
                "id": ids[i],
                "content": docs[i],
                "metadata": metas[i],
                "distance": distances[i],
            }
            for i in range(len(ids))
        ]

    def delete(self, id: str) -> None:
        """Remove a document permanently."""
        self._collection.delete(ids=[id])

    def update_metadata(self, id: str, metadata: dict) -> None:
        """Merge new metadata keys into an existing document."""
        self._collection.update(ids=[id], metadatas=[metadata])

    def count(self) -> int:
        """Total documents in the collection."""
        return self._collection.count()

    def heartbeat(self) -> bool:
        """Return True if the ChromaDB server is reachable."""
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _build_where(where: dict) -> dict:
    """Convert a flat filter dict into ChromaDB's ``$and`` format.

    A single-key dict is passed through unchanged.  Multiple keys are
    wrapped in ``{"$and": [{k: v}, ...]}`` because ChromaDB requires an
    explicit logical operator for compound filters.
    """
    if len(where) <= 1:
        return where
    return {"$and": [{k: v} for k, v in where.items()]}
