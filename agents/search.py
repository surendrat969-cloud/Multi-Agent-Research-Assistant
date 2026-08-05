"""Search Agent: gathers web-style synthesized information via the LLM."""
from __future__ import annotations

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState
from utils.helpers import truncate


class SearchAgent(BaseAgent):
    name = "Search Agent"
    description = "Collects relevant synthesized information for each sub-task."

    def run(self, state: ResearchState) -> ResearchState:
        results: list[str] = []
        for task in state.tasks:
            if task.source == "rag":
                continue
            prompt = f"""You are a research search assistant. Provide 3-5 concise, factual bullet points
of relevant information about this research sub-task. Be specific and informative.

Sub-task: {task.description}
Overall topic: {state.query}
"""
            try:
                text = safe_invoke(prompt, temperature=0.3)
                results.append(f"## {task.description}\n{text}")
            except Exception:  # noqa: BLE001
                continue
        state.search_results = results
        return state
