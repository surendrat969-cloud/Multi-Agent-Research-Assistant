"""Centralized application configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env once at import time.
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    gemini_model: str = field(default_factory=lambda: _env("GEMINI_MODEL", "gemini-flash-latest"))
    embedding_model: str = field(default_factory=lambda: _env("EMBEDDING_MODEL", "models/embedding-001"))
    app_name: str = field(default_factory=lambda: _env("APP_NAME", "ResearchMind AI"))
    app_env: str = field(default_factory=lambda: _env("APP_ENV", "production"))
    db_path: str = field(default_factory=lambda: _env("DB_PATH", "database/researchmind.db"))
    faiss_path: str = field(default_factory=lambda: _env("FAISS_PATH", "faiss_index"))
    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))
    log_file: str = field(default_factory=lambda: _env("LOG_FILE", "logs/app.log"))
    secret_key: str = field(default_factory=lambda: _env("SECRET_KEY", "change-this-secret-key-in-production"))
    session_ttl_hours: int = field(default_factory=lambda: int(_env("SESSION_TTL_HOURS", "24")))

    @property
    def db_path_abs(self) -> Path:
        p = Path(self.db_path)
        return p if p.is_absolute() else ROOT_DIR / p

    @property
    def faiss_path_abs(self) -> Path:
        p = Path(self.faiss_path)
        return p if p.is_absolute() else ROOT_DIR / p

    @property
    def log_file_abs(self) -> Path:
        p = Path(self.log_file)
        return p if p.is_absolute() else ROOT_DIR / p

    @property
    def is_configured(self) -> bool:
        return bool(self.gemini_api_key) and "your_gemini_api_key_here" not in self.gemini_api_key


settings = Settings()
