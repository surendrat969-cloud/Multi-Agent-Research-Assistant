"""FAISS vector store wrapper with persistence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np

from config import settings
from rag.embeddings import embed_texts, embed_query
from utils.logger import logger

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None


class FAISSStore:
    """In-memory + disk-persisted FAISS index for semantic search."""

    def __init__(self) -> None:
        self.index = None  # type: ignore[assignment]
        self.chunks: list[str] = []
        self.dim: int = 0
        self._path = settings.faiss_path_abs

    # ---- building -----------------------------------------------------------
    def build(self, texts: list[str]) -> None:
        if not texts or faiss is None:
            logger.warning("FAISS unavailable or no texts; skipping index build")
            return
        vectors = embed_texts(texts)
        self.dim = vectors.shape[1]
        self.index = faiss.IndexFlatL2(self.dim)
        self.index.add(vectors)
        self.chunks = texts
        self.save()
        logger.info("FAISS index built with %d vectors (dim=%d)", len(texts), self.dim)

    def add(self, texts: list[str]) -> None:
        if not texts:
            return
        if faiss is None:
            self.chunks.extend(texts)
            return
        if self.index is None:
            self.build(texts)
            return
        vectors = embed_texts(texts)
        self.index.add(vectors)
        self.chunks.extend(texts)
        self.save()

    # ---- search -------------------------------------------------------------
    def search(self, query: str, k: int = 5) -> list[str]:
        if not self.chunks:
            return []
        if faiss is None or self.index is None:
            # Fallback: naive keyword overlap
            return _keyword_fallback(self.chunks, query, k)
        qv = embed_query(query)
        k = min(k, len(self.chunks))
        distances, indices = self.index.search(qv, k)
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                results.append(self.chunks[idx])
        return results

    # ---- persistence --------------------------------------------------------
    def save(self) -> None:
        if faiss is None or self.index is None:
            return
        try:
            self._path.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self._path / "index.faiss"))
            (self._path / "chunks.json").write_text(json.dumps(self.chunks), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to persist FAISS index: %s", exc)

    def load(self) -> bool:
        if faiss is None:
            return False
        idx_file = self._path / "index.faiss"
        chunks_file = self._path / "chunks.json"
        if not idx_file.exists() or not chunks_file.exists():
            return False
        try:
            self.index = faiss.read_index(str(idx_file))
            self.chunks = json.loads(chunks_file.read_text(encoding="utf-8"))
            self.dim = self.index.d
            logger.info("Loaded FAISS index with %d vectors", len(self.chunks))
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load FAISS index: %s", exc)
            return False

    def clear(self) -> None:
        self.index = None
        self.chunks = []
        try:
            if self._path.exists():
                for f in self._path.glob("*"):
                    f.unlink()
        except Exception:  # noqa: BLE001
            pass

    @property
    def size(self) -> int:
        return len(self.chunks)


def _keyword_fallback(chunks: list[str], query: str, k: int) -> list[str]:
    qwords = set(query.lower().split())
    scored = []
    for c in chunks:
        cwords = set(c.lower().split())
        score = len(qwords & cwords)
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k] if _ > 0]


# Module-level singleton used across the app
store = FAISSStore()
