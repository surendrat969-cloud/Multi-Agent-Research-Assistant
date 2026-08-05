"""Research service: runs the agent pipeline, processes files, persists reports."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from agents.orchestrator import ResearchPipeline
from database import FileRepository, ReportRepository
from models.schemas import ReportRecord, ResearchState, UploadedFileRecord
from rag.document_loader import extract_text, file_type
from rag.embeddings import chunk_text
from rag.vector_store import store
from utils.helpers import estimate_reading_time, generate_id, now_iso, slugify, word_count
from utils.logger import logger


class FileService:
    """Handles uploads, extraction, chunking, and FAISS indexing."""

    @staticmethod
    def process_upload(upload_file, user_id: str) -> Optional[UploadedFileRecord]:
        """Process a Streamlit UploadedFile: save temp, extract, index, persist."""
        if upload_file is None:
            return None
        suffix = Path(upload_file.name).suffix
        tmp = Path("data") / f"{generate_id()}{suffix}"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "wb") as f:
            f.write(upload_file.getbuffer())
        try:
            text = extract_text(str(tmp))
        finally:
            tmp.unlink(missing_ok=True)

        if not text.strip():
            logger.warning("No text extracted from %s", upload_file.name)
            return None

        # Index into FAISS
        chunks = chunk_text(text)
        store.add(chunks)

        rec = UploadedFileRecord(
            id=generate_id("file"),
            user_id=user_id,
            filename=upload_file.name,
            file_type=file_type(upload_file.name) or "unknown",
            text_content=text[:50000],  # cap stored size
            created_at=now_iso(),
        )
        FileService.save(rec)
        return rec

    @staticmethod
    def save(rec: UploadedFileRecord) -> UploadedFileRecord:
        return FileRepository.save(rec)

    @staticmethod
    def list_for_user(user_id: str) -> list[UploadedFileRecord]:
        return FileRepository.list_for_user(user_id)

    # Note: do not define a `list` symbol here (it would shadow the builtin
    # `list` name and confuse type annotations). Use `FileService.list_for_user()`.

    @staticmethod
    def delete(file_id: str) -> bool:
        return FileRepository.delete(file_id)

    @staticmethod
    def rebuild_index(files: list[UploadedFileRecord]) -> int:
        """Rebuild the FAISS index from stored files."""
        store.clear()
        total_chunks = 0
        for f in files:
            chunks = chunk_text(f.text_content)
            store.add(chunks)
            total_chunks += len(chunks)
        return total_chunks


class ResearchService:
    """Runs the multi-agent pipeline and persists the report."""

    def __init__(self, pipeline: Optional[ResearchPipeline] = None) -> None:
        self.pipeline = pipeline or ResearchPipeline()

    def run(self, user_id: str, query: str) -> ResearchState:
        start = time.perf_counter()
        state = self.pipeline.run(query)
        duration = time.perf_counter() - start
        state.metadata["duration_sec"] = round(duration, 2)
        state.metadata["word_count"] = word_count(state.improved_report or state.report)
        state.metadata["reading_time_min"] = estimate_reading_time(state.improved_report or state.report)
        state.metadata["difficulty"] = _estimate_difficulty(state)

        # Persist the report
        rec = ReportRecord(
            id=generate_id("rep"),
            user_id=user_id,
            title=_derive_title(query),
            query=query,
            content=state.improved_report or state.report,
            citations=state.citations,
            tags=state.keywords,
            duration_sec=round(duration, 2),
            created_at=now_iso(),
            updated_at=now_iso(),
        )
        ReportRepository.create(rec)
        state.metadata["report_id"] = rec.id
        return state


def _derive_title(query: str) -> str:
    words = query.strip().split()
    if len(words) <= 6:
        return query.strip().title()
    return " ".join(words[:6]).title() + " …"


def _estimate_difficulty(state: ResearchState) -> str:
    words = state.metadata.get("word_count", 0)
    conf = state.confidence
    if words > 2500 or conf < 0.4:
        return "Advanced"
    if words > 1200:
        return "Intermediate"
    return "Beginner"
