## 1. Configuration

- [x] 1.1 Create `src/memories/config.py` — Define `Settings` class extending `pydantic_settings.BaseSettings` with fields: chromadb_host (str, "localhost"), chromadb_port (int, 8000), collection_name (str, "memories"), default_limit (int, 10), min_confidence (float, 0.3), decay_half_life_hours (float, 720). Configure `model_config` with `env_file=".env"`.

## 2. Data Models

- [x] 2.1 Create `src/memories/models.py` — Define enums: `DecayPolicy` (stable, contextual, reinforceable), `OutputFormat` (json, text). Define Pydantic models: `MemoryCreate` (content: str, agent: str="", personality: str="", project: str="", type: str="", global_: bool=False, decay_policy: DecayPolicy=DecayPolicy.STABLE), `MemoryResponse` (id: str, content: str, agent: str, personality: str, project: str, type: str, global_: bool, decay_policy: DecayPolicy, confidence: float, created_at: str, last_reinforced_at: str=""), `SearchResultItem` (extends MemoryResponse with similarity: float), `SearchResponse` (results: list[SearchResultItem], count: int).

## 3. Vector Store Protocol

- [x] 3.1 Create `src/memories/stores/vector_store.py` — Define `VectorStore` Protocol with methods: `store(self, id: str, content: str, metadata: dict) -> None`, `get(self, id: str) -> dict | None`, `search(self, query: str, n_results: int, where: dict | None = None) -> list[dict]`, `delete(self, id: str) -> None`, `update_metadata(self, id: str, metadata: dict) -> None`, `count(self) -> int`, `heartbeat(self) -> bool`.

## 4. ChromaDB Adapter

- [x] 4.1 Create `src/memories/stores/chromadb_adapter.py` — Implement `ChromaDBAdapter` class that satisfies the VectorStore Protocol. Constructor takes host and port, creates `chromadb.HttpClient`, and calls `get_or_create_collection`. Implement all Protocol methods using ChromaDB's collection API. Handle compound `where` filters by wrapping multiple conditions in `{"$and": [...]}`. *(Requires running ChromaDB for manual verification)*
- [x] 4.2 Manually verify adapter against running ChromaDB: store a document, retrieve it by ID, search for it, update its metadata, delete it.
