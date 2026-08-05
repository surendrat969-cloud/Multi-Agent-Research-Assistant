"""Interview Agent: generates interview questions and model answers."""
from __future__ import annotations

import json
import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class InterviewAgent(BaseAgent):
    name = "Interview Agent"
    description = "Generates interview questions and answers on the research topic."

    def run(self, state: ResearchState) -> ResearchState:
        prompt = f"""You are a technical interviewer. Generate 8 interview questions (mix of conceptual and applied)
about the topic below, each with a concise model answer (2-4 sentences).
Return ONLY a JSON array of objects with keys "question" and "answer".

Topic: {state.query}
"""
        raw = safe_invoke(prompt, temperature=0.4)
        items: list[dict[str, str]] = []
        try:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                items = json.loads(match.group(0))
        except Exception:  # noqa: BLE001
            pass
        if not items:
            items = [{"question": f"What is {state.query}?", "answer": "See the report for a detailed explanation."}]
        state.interview = items
        return state
