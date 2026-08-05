"""Quiz Agent: generates multiple-choice questions with answers."""
from __future__ import annotations

import json
import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class QuizAgent(BaseAgent):
    name = "Quiz Agent"
    description = "Generates MCQs with answers to test understanding."

    def run(self, state: ResearchState) -> ResearchState:
        prompt = f"""You are a quiz creator. Generate 8 multiple-choice questions about the topic below.
Each question has 4 options and one correct answer (0-indexed).
Return ONLY a JSON array of objects: {{"question": str, "options": [4 strings], "answer": int}}

Topic: {state.query}
"""
        raw = safe_invoke(prompt, temperature=0.4)
        quiz: list[dict] = []
        try:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                quiz = json.loads(match.group(0))
        except Exception:  # noqa: BLE001
            pass
        if not quiz:
            quiz = [
                {
                    "question": f"What best describes {state.query}?",
                    "options": ["A", "B", "C", "D"],
                    "answer": 0,
                }
            ]
        state.quiz = quiz
        return state
