"""Unit tests for helpers, models, and RAG chunking."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import slugify, hash_password, estimate_reading_time, word_count, generate_id
from models.schemas import ResearchState, ResearchTask
from rag.embeddings import chunk_text
from rag.document_loader import file_type


def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("  Multi   Word--Test  ") == "multi-word-test"


def test_hash_password_consistent():
    assert hash_password("abc") == hash_password("abc")
    assert hash_password("abc") != hash_password("abcd")


def test_reading_time():
    text = " ".join(["word"] * 400)
    assert estimate_reading_time(text) == 2  # 400/200


def test_word_count():
    assert word_count("one two three") == 3


def test_generate_id_unique():
    ids = {generate_id() for _ in range(50)}
    assert len(ids) == 50


def test_research_state_defaults():
    s = ResearchState(query="ai")
    assert s.tasks == []
    assert s.confidence == 0.0
    assert s.report == ""


def test_research_task():
    t = ResearchTask(id="t1", description="explore x")
    assert t.source == "web"


def test_chunk_text_short():
    assert chunk_text("short text") == ["short text"]


def test_chunk_text_long():
    text = " ".join(["word"] * 2000)
    chunks = chunk_text(text, size=500, overlap=50)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_file_type():
    assert file_type("doc.pdf") == "pdf"
    assert file_type("doc.docx") == "docx"
    assert file_type("doc.txt") == "txt"
    assert file_type("doc.zip") is None
