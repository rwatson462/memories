"""Domain models and enums for the memories service.

All data shapes exchanged between the CLI, service, and store layers
are defined here so there is a single source of truth.
"""

from enum import Enum

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DecayPolicy(str, Enum):
    """Controls how a memory's confidence decays over time."""

    STABLE = "stable"
    CONTEXTUAL = "contextual"
    REINFORCEABLE = "reinforceable"


class OutputFormat(str, Enum):
    """CLI output format selector."""

    JSON = "json"
    TEXT = "text"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class MemoryCreate(BaseModel):
    """Input payload for creating a new memory."""

    content: str
    agent: str = ""
    personality: str = ""
    project: str = ""
    type: str = ""
    global_: bool = False
    decay_policy: DecayPolicy = DecayPolicy.STABLE


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class MemoryResponse(BaseModel):
    """A single stored memory returned to the caller."""

    id: str
    content: str
    agent: str
    personality: str
    project: str
    type: str
    global_: bool
    decay_policy: DecayPolicy
    confidence: float
    created_at: str
    last_reinforced_at: str = ""


class SearchResultItem(MemoryResponse):
    """MemoryResponse augmented with a similarity score from search."""

    similarity: float


class SearchResponse(BaseModel):
    """Wrapper for a list of search results."""

    results: list[SearchResultItem]
    count: int
