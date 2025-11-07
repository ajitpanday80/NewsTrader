"""
Configuration management for NewsTrader application.
Loads settings from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    alpha_vantage_api_key: str
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    # Signal TTL Configuration
    signal_ttl_minutes: int = 30

    # Job Intervals
    cleanup_interval_minutes: int = 5
    news_fetch_interval_minutes: int = 5

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Logging
    log_level: str = "INFO"

    # Paths
    data_dir: Path = Path("data")
    active_dir: Path = Path("data/active")
    backup_dir: Path = Path("data/backups")
    logs_dir: Path = Path("logs")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
