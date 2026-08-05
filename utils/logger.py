"""Singleton logger setup for the whole application."""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler

from config import settings

_INITIALIZED = False


def get_logger(name: str = "researchmind") -> logging.Logger:
    """Return a configured logger. Safe to call multiple times."""
    global _INITIALIZED
    logger = logging.getLogger(name)
    if _INITIALIZED:
        return logger

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # File handler (best-effort: don't crash if dir missing)
    try:
        settings.log_file_abs.parent.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(settings.log_file_abs, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:  # noqa: BLE001
        pass

    _INITIALIZED = True
    return logger


logger = get_logger()
