"""Core business logic for memory operations.

Orchestrates all create / search / get / reinforce / delete / status
operations.  Depends only on the VectorStore protocol and Settings —
never imports ChromaDB directly.
"""

import uuid
from datetime import datetime, timezone

from memories.config import Settings
from memories.models import (
    DecayPolicy,
    MemoryCreate,
    MemoryResponse,
    SearchResponse,
    SearchResultItem,
)
from memories.services.decay import compute_confidence
from memories.stores.vector_store import VectorStore


# ---------------------------------------------------------------------------
# Custom exceptions — the CLI maps these to user-facing error output.
# ---------------------------------------------------------------------------

class MemoryNotFoundError(Exception):
    """Raised when a memory ID does not exist or is soft-deleted."""

    def __init__(self, id: str) -> None:
        self.id = id
        super().__init__(f"Memory '{id}' not found")


class InvalidOperationError(Exception):
    """Raised when an operation is not allowed for the given memory state."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class MemoryService:
    """Business logic layer sitting between the CLI and the VectorStore."""

    def __init__(self, store: VectorStore, settings: Settings) -> None:
        self._store = store
        self._settings = settings

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_memory(self, data: MemoryCreate) -> MemoryResponse:
        """Store a new memory and return it with confidence 1.0.

        Generates a UUID, stamps created_at, and persists via the
        VectorStore.  A just-created memory always has full confidence.
        """
        memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        metadata = {
            "agent": data.agent,
            "personality": data.personality,
            "project": data.project,
            "type": data.type,
            "global_": data.global_,
            "decay_policy": data.decay_policy.value,
            "created_at": now,
            "last_reinforced_at": "",
            "deleted": False,
        }

        self._store.store(memory_id, data.content, metadata)

        return MemoryResponse(
            id=memory_id,
            content=data.content,
            agent=data.agent,
            personality=data.personality,
            project=data.project,
            type=data.type,
            global_=data.global_,
            decay_policy=data.decay_policy,
            confidence=1.0,
            created_at=now,
            last_reinforced_at="",
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_memories(
        self,
        query: str,
        agent: str = "",
        personality: str = "",
        project: str = "",
        type_: str = "",
        global_: bool | None = None,
        limit: int = 10,
        min_confidence: float = 0.3,
    ) -> SearchResponse:
        """Semantic search with metadata filters and confidence gating.

        Builds a where-clause (always excluding deleted), queries the
        VectorStore, computes confidence per result, and drops anything
        below min_confidence.
        """
        where: dict = {"deleted": False}
        if agent:
            where["agent"] = agent
        if personality:
            where["personality"] = personality
        if project:
            where["project"] = project
        if type_:
            where["type"] = type_
        if global_ is not None:
            where["global_"] = global_

        raw_results = self._store.search(query, n_results=limit, where=where)

        items: list[SearchResultItem] = []
        for r in raw_results:
            meta = r["metadata"]
            confidence = self._compute_confidence_from_meta(meta)

            if confidence < min_confidence:
                continue

            items.append(
                SearchResultItem(
                    id=r["id"],
                    content=r["content"],
                    agent=meta.get("agent", ""),
                    personality=meta.get("personality", ""),
                    project=meta.get("project", ""),
                    type=meta.get("type", ""),
                    global_=meta.get("global_", False),
                    decay_policy=DecayPolicy(meta["decay_policy"]),
                    confidence=confidence,
                    created_at=meta.get("created_at", ""),
                    last_reinforced_at=meta.get("last_reinforced_at", ""),
                    similarity=r.get("distance", 0.0),
                )
            )

        return SearchResponse(results=items, count=len(items))

    # ------------------------------------------------------------------
    # Get
    # ------------------------------------------------------------------

    def get_memory(self, id: str) -> MemoryResponse:
        """Retrieve a single memory by ID.

        Raises MemoryNotFoundError if the ID is missing or soft-deleted.
        """
        doc = self._store.get(id)
        if doc is None or doc["metadata"].get("deleted", False):
            raise MemoryNotFoundError(id)

        meta = doc["metadata"]
        confidence = self._compute_confidence_from_meta(meta)

        return MemoryResponse(
            id=doc["id"],
            content=doc["content"],
            agent=meta.get("agent", ""),
            personality=meta.get("personality", ""),
            project=meta.get("project", ""),
            type=meta.get("type", ""),
            global_=meta.get("global_", False),
            decay_policy=DecayPolicy(meta["decay_policy"]),
            confidence=confidence,
            created_at=meta.get("created_at", ""),
            last_reinforced_at=meta.get("last_reinforced_at", ""),
        )

    # ------------------------------------------------------------------
    # Reinforce
    # ------------------------------------------------------------------

    def reinforce_memory(self, id: str) -> dict:
        """Reset decay timer for a reinforceable memory.

        Only memories with decay_policy="reinforceable" can be reinforced.
        Updates last_reinforced_at to now and returns confirmation.
        """
        doc = self._store.get(id)
        if doc is None or doc["metadata"].get("deleted", False):
            raise MemoryNotFoundError(id)

        policy = doc["metadata"].get("decay_policy", "")
        if policy != DecayPolicy.REINFORCEABLE.value:
            # Policy-specific messages per spec so the user knows *why* it failed.
            if policy == DecayPolicy.STABLE.value:
                msg = "Memory has stable decay policy, reinforcement has no effect"
            elif policy == DecayPolicy.CONTEXTUAL.value:
                msg = "Memory has contextual decay policy, reinforcement is not supported"
            else:
                msg = f"Memory has {policy} decay policy, cannot be reinforced"
            raise InvalidOperationError(msg)

        now = datetime.now(timezone.utc).isoformat()
        self._store.update_metadata(id, {"last_reinforced_at": now})

        return {"id": id, "reinforced_at": now, "confidence": 1.0}

    # ------------------------------------------------------------------
    # Delete (soft)
    # ------------------------------------------------------------------

    def delete_memory(self, id: str) -> dict:
        """Soft-delete a memory by setting its deleted flag.

        Raises MemoryNotFoundError if the ID doesn't exist, and
        InvalidOperationError if it's already deleted.
        """
        doc = self._store.get(id)
        if doc is None:
            raise MemoryNotFoundError(id)

        if doc["metadata"].get("deleted", False):
            raise InvalidOperationError(f"Memory '{id}' is already deleted")

        self._store.update_metadata(id, {"deleted": True})

        return {"id": id, "deleted": True}

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Check VectorStore health and return collection stats."""
        healthy = self._store.heartbeat()
        count = self._store.count() if healthy else 0

        return {
            "status": "healthy" if healthy else "unhealthy",
            "host": f"{self._settings.chromadb_host}:{self._settings.chromadb_port}",
            "collection": self._settings.collection_name,
            "count": count,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_confidence_from_meta(self, meta: dict) -> float:
        """Extract timestamps from metadata and delegate to the decay module."""
        created_at = datetime.fromisoformat(meta["created_at"])

        last_reinforced_raw = meta.get("last_reinforced_at", "")
        last_reinforced_at = (
            datetime.fromisoformat(last_reinforced_raw)
            if last_reinforced_raw
            else None
        )

        return compute_confidence(
            decay_policy=meta["decay_policy"],
            created_at=created_at,
            last_reinforced_at=last_reinforced_at,
            half_life_hours=self._settings.decay_half_life_hours,
        )
