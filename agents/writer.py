"""Writer Agent: produces a structured professional research report."""
from __future__ import annotations

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class WriterAgent(BaseAgent):
    name = "Writer Agent"
    description = "Generates a professional, structured research report."

    SECTIONS = [
        "Abstract",
        "Executive Summary",
        "Introduction",
        "Key Findings",
        "Advantages",
        "Disadvantages",
        "Limitations",
        "Real-world Applications",
        "Future Scope",
        "Research Timeline",
        "Technology Stack",
        "SWOT Analysis",
        "Conclusion",
    ]

    def run(self, state: ResearchState) -> ResearchState:
        facts = "\n".join(f"- {f}" for f in state.verified_facts[:60]) or "No verified facts available."
        sections = "\n".join(f"- {s}" for s in self.SECTIONS)
        prompt = f"""You are an expert research writer. Using the verified facts below, write a comprehensive,
professional research report on: "{state.query}".

Include these sections:
{sections}

Guidelines:
- Use Markdown headings (##) for each section.
- Be specific and cite facts from the verified list.
- Confidence score: {state.confidence}
- Keep it well-structured and readable.

Verified Facts:
{facts}
"""
        report = safe_invoke(prompt, temperature=0.5)
        state.report = report
        return state
