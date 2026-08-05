"""Integration tests for database repositories and exports."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Use a temp DB to avoid polluting the real one
tmpdir = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(tmpdir, "test.db")

from config import settings  # noqa: E402
# Reimport after env override isn't trivial for frozen dataclass; set path attribute via env at process start.
# For the test we use the live DB path override through the repository init which reads settings.db_path_abs.

from database import init_db, UserRepository, ReportRepository  # noqa: E402
from models.schemas import ReportRecord, ResearchState  # noqa: E402
from utils.helpers import generate_id, now_iso  # noqa: E402


def _user():
    import uuid
    unique = f"tester_{uuid.uuid4().hex[:6]}"
    return UserRepository.create(unique, f"{unique}@example.com", "secret123")


def test_user_signup_and_login():
    init_db()
    user = _user()
    assert user.username.startswith("tester_")
    found = UserRepository.verify(user.username, "secret123")
    assert found is not None
    assert UserRepository.verify(user.username, "wrong") is None


def test_report_crud():
    init_db()
    user = _user()
    rec = ReportRecord(
        id=generate_id("rep"),
        user_id=user.id,
        title="Test Report",
        query="test query",
        content="body",
        citations=["c1"],
        tags=["ai"],
        created_at=now_iso(),
        updated_at=now_iso(),
    )
    ReportRepository.create(rec)
    listed = ReportRepository.list_for_user(user.id)
    assert any(r.title == "Test Report" for r in listed)
    got = ReportRepository.get(rec.id)
    assert got.citations == ["c1"]
    ReportRepository.update(rec.id, bookmarked=True)
    assert ReportRepository.get(rec.id).bookmarked is True
    assert ReportRepository.delete(rec.id) is True


def test_exports_markdown_and_text():
    from exports.exporters import to_markdown, to_text  # noqa: E402
    state = ResearchState(query="topic", report="# Heading\nbody text", citations=["## APA\nref1"])
    md = to_markdown(state)
    assert "topic" in md and "ref1" in md
    txt = to_text(state)
    assert "#" not in txt
