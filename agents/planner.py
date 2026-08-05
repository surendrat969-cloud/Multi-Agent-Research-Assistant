"""Planner Agent: decomposes a query into research sub-tasks."""
from __future__ import annotations

import json
import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState, ResearchTask
from utils.helpers import generate_id


class PlannerAgent(BaseAgent):
    name = "Planner Agent"
    description = "Breaks the user's research query into actionable sub-tasks."

    def run(self, state: ResearchState) -> ResearchState:
        prompt = f"""You are a research planner. Break the following research query into 3 to 6 focused sub-tasks.
Return ONLY a JSON array of objects with keys "description" and "source" where source is one of: web, rag, both.

Query: "{state.query}"
"""
        raw = safe_invoke(prompt, temperature=0.2)
        tasks = _parse_tasks(raw)
        if not tasks:
            tasks = [
                ResearchTask(id=generate_id("task"), description=f"Overview of {state.query}", source="both"),
                ResearchTask(id=generate_id("task"), description=f"Key concepts and definitions for {state.query}", source="web"),
                ResearchTask(id=generate_id("task"), description=f"Recent developments in {state.query}", source="web"),
            ]
        state.tasks = tasks
        return state


def _parse_tasks(raw: str) -> list[ResearchTask]:
    # Tolerant JSON extraction
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    tasks = []
    for item in data:
        desc = item.get("description", "").strip()
        if not desc:
            continue
        tasks.append(
            ResearchTask(
                id=generate_id("task"),
                description=desc,
                source=item.get("source", "web"),
            )
        )
    return tasks
