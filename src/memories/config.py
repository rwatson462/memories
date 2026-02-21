"""Application configuration loaded from environment variables.

Uses pydantic-settings to read env vars (and .env file) with sensible
defaults for local development.  Import `settings` from this module
wherever configuration values are needed.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration knobs for the memories service."""

    # ChromaDB connection
    chromadb_host: str = "localhost"
    chromadb_port: int = 8000

    # Collection and query defaults
    collection_name: str = "memories"
    default_limit: int = 10

    # Confidence / decay tuning
    min_confidence: float = 0.3
    decay_half_life_hours: float = 720  # 30 days

    model_config = {"env_file": ".env"}


# Singleton — import this, not the class.
settings = Settings()
