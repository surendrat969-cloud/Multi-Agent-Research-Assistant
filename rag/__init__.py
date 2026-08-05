"""RAG package: document loading, chunking, embeddings, FAISS search."""
from rag.document_loader import extract_text, file_type
from rag.embeddings import chunk_text, embed_texts, embed_query, get_embedder
from rag.vector_store import FAISSStore, store

__all__ = [
    "extract_text", "file_type",
    "chunk_text", "embed_texts", "embed_query", "get_embedder",
    "FAISSStore", "store",
]
