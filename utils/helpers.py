"""Shared utilities: timing, text helpers, ID generation."""
from __future__ import annotations

import hashlib
import re
import time
import uuid
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Iterator

from utils.logger import logger


def generate_id(prefix: str = "") -> str:
    """Short unique id with optional prefix."""
    short = uuid.uuid4().hex[:12]
    return f"{prefix}_{short}" if prefix else short


def now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str, max_len: int = 50) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    text = re.sub(r"[\s-]+", "-", text)
    return text[:max_len].strip("-") or "research"


def truncate(text: str, max_chars: int = 2000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " …"


def hash_password(password: str, salt: str = "researchmind") -> str:
    """Simple SHA-256 hash with salt. Suitable for demo, not production-grade."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    words = len(text.split())
    return max(1, round(words / wpm))


def word_count(text: str) -> int:
    return len(text.split())


@contextmanager
def timed(label: str) -> Iterator[float]:
    """Context manager that logs elapsed time for a block."""
    start = time.perf_counter()
    try:
        yield start
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"⏱ {label} took {elapsed:.3f}s")


def log_execution(agent_name: str) -> Callable:
    """Decorator: log agent execution time and errors."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            logger.info(f"▶ {agent_name} started")
            try:
                result = fn(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"✔ {agent_name} completed in {elapsed:.3f}s")
                return result
            except Exception as exc:  # noqa: BLE001
                elapsed = time.perf_counter() - start
                logger.error(f"✖ {agent_name} failed after {elapsed:.3f}s: {exc}")
                raise

        return wrapper

    return decorator
