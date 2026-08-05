"""Extract text from PDF, DOCX, and TXT uploads."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from utils.logger import logger


def extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_pdf(path: str) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyPDF2 is required to read PDFs") from exc
    reader = PdfReader(path)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages).strip()


def extract_docx(path: str) -> str:
    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("python-docx is required to read DOCX") from exc
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(path: str) -> str:
    """Dispatch by extension. Returns empty string on unknown types."""
    p = Path(path)
    ext = p.suffix.lower()
    try:
        if ext == ".txt":
            return extract_txt(path)
        if ext == ".pdf":
            return extract_pdf(path)
        if ext in (".docx", ".doc"):
            return extract_docx(path)
        logger.warning("Unsupported file type: %s", ext)
        return ""
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract %s: %s", path, exc)
        raise


def file_type(path: str) -> Optional[str]:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".txt":
        return "txt"
    if ext in (".docx", ".doc"):
        return "docx"
    return None
