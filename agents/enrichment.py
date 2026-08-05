"""Enrichment Agent: produces summary, keywords, FAQ, glossary, SWOT, learning resources."""
from __future__ import annotations

import json
import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class EnrichmentAgent(BaseAgent):
    name = "Enrichment Agent"
    description = "Adds executive summary, keywords, FAQ, glossary, SWOT, and resources."

    def run(self, state: ResearchState) -> ResearchState:
        report = state.improved_report or state.report
        prompt = f"""You are a research enrichment assistant. From the report below, produce a JSON object with these keys:
- "summary": a 4-6 sentence executive summary
- "abstract": a 2-3 sentence abstract
- "keywords": list of 8-12 keywords
- "faq": list of {{"question": str, "answer": str}} (6 items)
- "glossary": list of {{"term": str, "definition": str}} (8 items)
- "swot": {{"strengths": [str], "weaknesses": [str], "opportunities": [str], "threats": [str]}}
- "formulas": list of {{"name": str, "formula": str}} (if applicable, else empty)
- "learning_resources": list of {{"title": str, "type": str, "url": str}}
- "github_resources": list of {{"title": str, "url": str}}
- "youtube_resources": list of {{"title": str, "url": str}}
- "books": list of {{"title": str, "author": str}}
- "papers": list of {{"title": str, "authors": str, "year": str}}
- "future_scope": list of str
- "limitations": list of str
- "advantages": list of str
- "disadvantages": list of str
- "applications": list of str
- "timeline": list of {{"year": str, "event": str}}
- "tech_stack": list of str

Return ONLY the JSON object.

Topic: {state.query}

Report:
{report[:4000]}
"""
        raw = safe_invoke(prompt, temperature=0.4)
        data: dict = {}
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
        except Exception:  # noqa: BLE001
            pass

        state.summary = data.get("summary", "")
        state.keywords = list(data.get("keywords", []))
        state.metadata["enrichment"] = data
        return state
