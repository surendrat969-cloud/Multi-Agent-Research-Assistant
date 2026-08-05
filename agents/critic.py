"""Critic Agent: reviews and improves clarity, coherence, and quality."""
from __future__ import annotations

import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class CriticAgent(BaseAgent):
    name = "Critic Agent"
    description = "Reviews the draft report and improves clarity and structure."

    def run(self, state: ResearchState) -> ResearchState:
        if not state.report:
            state.improved_report = ""
            return state
        prompt = f"""You are a senior research editor. Improve the following research report for clarity,
flow, grammar, and professional tone. Preserve all sections and factual content. Remove redundancy.
Return the improved full report in Markdown.

Report:
{state.report}
"""
        improved = safe_invoke(prompt, temperature=0.4)
        # Ensure it's non-empty; otherwise keep original
        state.improved_report = improved if len(improved) > 200 else state.report
        # Compute a simple quality score
        original_words = len(state.report.split())
        improved_words = len(state.improved_report.split())
        state.metadata["quality_score"] = round(
            min(10.0, 5.0 + (improved_words / max(original_words, 1)) * 2.0), 2
        )
        return state
