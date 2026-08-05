"""Presentation Agent: generates slide outlines for an auto PPT."""
from __future__ import annotations

import json
import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class PresentationAgent(BaseAgent):
    name = "Presentation Agent"
    description = "Creates a structured slide deck outline from the report."

    def run(self, state: ResearchState) -> ResearchState:
        report = state.improved_report or state.report
        prompt = f"""You are a presentation designer. Create an 8-10 slide deck outline for the research topic below.
Return ONLY a JSON array of objects with keys "title" and "bullets" (bullets is a list of 3-5 short strings).

Topic: {state.query}

Report:
{report[:3000]}
"""
        raw = safe_invoke(prompt, temperature=0.4)
        slides: list[dict] = []
        try:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                slides = json.loads(match.group(0))
        except Exception:  # noqa: BLE001
            pass
        if not slides:
            slides = [
                {"title": state.query, "bullets": ["Overview", "Key findings", "Conclusion"]},
                {"title": "Summary", "bullets": ["See full report for details"]},
            ]
        state.slides = slides
        return state
