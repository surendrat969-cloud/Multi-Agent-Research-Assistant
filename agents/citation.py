"""Citation Agent: generates references and citations in APA, MLA, IEEE."""
from __future__ import annotations

import json
import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState


class CitationAgent(BaseAgent):
    name = "Citation Agent"
    description = "Generates references in APA, MLA, and IEEE formats."

    def run(self, state: ResearchState) -> ResearchState:
        prompt = f"""You are a citation generator. Based on the research topic and report below, produce 6 plausible
academic-style references. Return JSON with keys "apa", "mla", "ieee" each being a list of citation strings.

Topic: {state.query}

Report excerpt:
{state.improved_report or state.report[:1500]}
"""
        raw = safe_invoke(prompt, temperature=0.3)
        apa, mla, ieee = [], [], []
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                apa = list(data.get("apa", []))
                mla = list(data.get("mla", []))
                ieee = list(data.get("ieee", []))
        except Exception:  # noqa: BLE001
            pass
        citations: list[str] = []
        if apa:
            citations.append("## APA\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(apa)))
        if mla:
            citations.append("## MLA\n" + "\n".join(f"{i+1}. {c}" for i, c in enumerate(mla)))
        if ieee:
            citations.append("## IEEE\n" + "\n".join(f"[{i+1}] {c}" for i, c in enumerate(ieee)))
        if not citations:
            citations = ["(No citations generated)"]
        state.citations = citations
        state.metadata["citations_apa"] = apa
        state.metadata["citations_mla"] = mla
        state.metadata["citations_ieee"] = ieee
        return state
