"""Data Access Objects for all database entities."""
from __future__ import annotations

import json
from typing import Any, Optional

from database.db import get_connection, init_db
from models.schemas import (
    ChatMessage, ReportRecord, UploadedFileRecord, User,
)
from utils.helpers import generate_id, hash_password, now_iso
from utils.logger import logger


class UserRepository:
    """CRUD for users."""

    @staticmethod
    def create(username: str, email: str, password: str) -> User:
        init_db()
        uid = generate_id("usr")
        user = User(
            id=uid,
            username=username,
            email=email,
            password_hash=hash_password(password),
            created_at=now_iso(),
        )
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?,?,?,?,?)",
                (user.id, user.username, user.email, user.password_hash, user.created_at),
            )
            conn.commit()
            logger.info("Created user %s", username)
            return user
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            return User(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            return User(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(uid: str) -> Optional[User]:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
            return User(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def verify(username: str, password: str) -> Optional[User]:
        user = UserRepository.get_by_username(username)
        if user and user.password_hash == hash_password(password):
            return user
        return None

    @staticmethod
    def reset_password(email: str, new_password: str) -> bool:
        conn = get_connection()
        try:
            cur = conn.execute(
                "UPDATE users SET password_hash=? WHERE email=?",
                (hash_password(new_password), email),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


class ReportRepository:
    """CRUD for research reports."""

    @staticmethod
    def create(rec: ReportRecord) -> ReportRecord:
        init_db()
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO reports
                (id, user_id, title, query, content, citations, tags, duration_sec,
                 bookmarked, favorite, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    rec.id, rec.user_id, rec.title, rec.query, rec.content,
                    json.dumps(rec.citations), json.dumps(rec.tags), rec.duration_sec,
                    int(rec.bookmarked), int(rec.favorite), rec.created_at, rec.updated_at,
                ),
            )
            conn.commit()
            return rec
        finally:
            conn.close()

    @staticmethod
    def list_for_user(user_id: str, search: str = "") -> list[ReportRecord]:
        conn = get_connection()
        try:
            if search:
                rows = conn.execute(
                    "SELECT * FROM reports WHERE user_id=? AND (title LIKE ? OR query LIKE ?) ORDER BY created_at DESC",
                    (user_id, f"%{search}%", f"%{search}%"),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM reports WHERE user_id=? ORDER BY created_at DESC",
                    (user_id,),
                ).fetchall()
            return [ReportRepository._row_to_rec(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get(report_id: str) -> Optional[ReportRecord]:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
            return ReportRepository._row_to_rec(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def update(report_id: str, **fields: Any) -> bool:
        if not fields:
            return False
        # Whitelist allowed columns
        allowed = {"title", "content", "citations", "tags", "duration_sec",
                   "bookmarked", "favorite", "updated_at"}
        sets, vals = [], []
        for k, v in fields.items():
            if k not in allowed:
                continue
            if k in ("citations", "tags"):
                v = json.dumps(v)
            if k in ("bookmarked", "favorite"):
                v = int(v)
            sets.append(f"{k}=?")
            vals.append(v)
        if not sets:
            return False
        vals.append(now_iso())
        sets.append("updated_at=?")
        vals.append(report_id)
        conn = get_connection()
        try:
            cur = conn.execute(f"UPDATE reports SET {', '.join(sets)} WHERE id=?", vals)
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def delete(report_id: str) -> bool:
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM reports WHERE id=?", (report_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def _row_to_rec(row) -> ReportRecord:  # type: ignore[no-untyped-def]
        d = dict(row)
        d["citations"] = json.loads(d.get("citations") or "[]")
        d["tags"] = json.loads(d.get("tags") or "[]")
        d["bookmarked"] = bool(d.get("bookmarked", 0))
        d["favorite"] = bool(d.get("favorite", 0))
        return ReportRecord(**d)


class ChatRepository:
    """Persistent chat history."""

    @staticmethod
    def add(user_id: str, session_id: str, role: str, content: str) -> ChatMessage:
        init_db()
        msg = ChatMessage(role=role, content=content, timestamp=now_iso())
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO chats (id, user_id, session_id, role, content, timestamp) VALUES (?,?,?,?,?,?)",
                (generate_id("msg"), user_id, session_id, role, content, msg.timestamp),
            )
            conn.commit()
            return msg
        finally:
            conn.close()

    @staticmethod
    def history(user_id: str, session_id: str, limit: int = 100) -> list[ChatMessage]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT role, content, timestamp FROM chats WHERE user_id=? AND session_id=? ORDER BY timestamp ASC LIMIT ?",
                (user_id, session_id, limit),
            ).fetchall()
            return [ChatMessage(role=r["role"], content=r["content"], timestamp=r["timestamp"]) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def sessions(user_id: str) -> list[dict[str, str]]:
        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT session_id, MIN(timestamp) as first, MAX(timestamp) as last,
                          (SELECT content FROM chats c2 WHERE c2.session_id=c.session_id AND c2.role='user'
                           ORDER BY c2.timestamp ASC LIMIT 1) as topic
                   FROM chats c WHERE user_id=? GROUP BY session_id ORDER BY last DESC""",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def delete_session(user_id: str, session_id: str) -> bool:
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM chats WHERE user_id=? AND session_id=?", (user_id, session_id))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


class FileRepository:
    """Uploaded file text storage (for RAG beyond the live session)."""

    @staticmethod
    def save(rec: UploadedFileRecord) -> UploadedFileRecord:
        init_db()
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO uploaded_files (id, user_id, filename, file_type, text_content, created_at) VALUES (?,?,?,?,?,?)",
                (rec.id, rec.user_id, rec.filename, rec.file_type, rec.text_content, rec.created_at),
            )
            conn.commit()
            return rec
        finally:
            conn.close()

    @staticmethod
    def list_for_user(user_id: str) -> list[UploadedFileRecord]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM uploaded_files WHERE user_id=? ORDER BY created_at DESC", (user_id,)
            ).fetchall()
            return [UploadedFileRecord(**dict(r)) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def delete(file_id: str) -> bool:
        conn = get_connection()
        try:
            cur = conn.execute("DELETE FROM uploaded_files WHERE id=?", (file_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


class FeedbackRepository:
    @staticmethod
    def add(user_id: str, report_id: str, rating: int, comment: str = "") -> None:
        init_db()
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO feedback (id, user_id, report_id, rating, comment, created_at) VALUES (?,?,?,?,?,?)",
                (generate_id("fb"), user_id, report_id, rating, comment, now_iso()),
            )
            conn.commit()
        finally:
            conn.close()
