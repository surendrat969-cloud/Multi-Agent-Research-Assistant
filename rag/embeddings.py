"""Chunking and embedding helpers for RAG."""
from __future__ import annotations

from typing import Iterable

import numpy as np

from utils.logger import logger

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Sentence-aware sliding window chunking."""
    if not text:
        return []
    words = text.split()
    if len(words) <= size:
        return [text.strip()]
    chunks: list[str] = []
    step = size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + size])
        if chunk:
            chunks.append(chunk)
        if i + size >= len(words):
            break
    logger.info("Chunked text into %d chunks", len(chunks))
    return chunks


def get_embedder():
    """Lazy import + build the Gemini embedding model."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from config import settings
    if not settings.is_configured:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
    )


def embed_texts(texts: Iterable[str]) -> np.ndarray:
    embedder = get_embedder()
    vecs = embedder.embed_documents(list(texts))
    return np.array(vecs, dtype="float32")


def embed_query(text: str) -> np.ndarray:
    embedder = get_embedder()
    vec = embedder.embed_query(text)
    return np.array([vec], dtype="float32")
