"""Pydantic data models used across agents and services."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ResearchTask(BaseModel):
    """A single sub-task produced by the Planner Agent."""
    id: str
    description: str
    source: str = "web"  # web | rag | both


class ResearchState(BaseModel):
    """Mutable state passed through the LangGraph agent pipeline."""
    query: str
    tasks: list[ResearchTask] = Field(default_factory=list)
    search_results: list[str] = Field(default_factory=list)
    rag_results: list[str] = Field(default_factory=list)
    verified_facts: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    report: str = ""
    improved_report: str = ""
    citations: list[str] = Field(default_factory=list)
    slides: list[dict[str, Any]] = Field(default_factory=list)
    interview: list[dict[str, str]] = Field(default_factory=list)
    quiz: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    agent_log: list[dict[str, Any]] = Field(default_factory=list)


class User(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    created_at: str


class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str
    timestamp: str = ""


class ReportRecord(BaseModel):
    id: str
    user_id: str
    title: str
    query: str
    content: str
    citations: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    duration_sec: float = 0.0
    bookmarked: bool = False
    favorite: bool = False
    created_at: str = ""
    updated_at: str = ""


class UploadedFileRecord(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    text_content: str
    created_at: str
