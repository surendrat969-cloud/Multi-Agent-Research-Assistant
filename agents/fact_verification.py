"""Fact Verification Agent: deduplicates, estimates confidence, flags uncertainty."""
from __future__ import annotations

import re

from agents.base import BaseAgent
from agents.llm import safe_invoke
from models.schemas import ResearchState
from utils.logger import logger


class FactVerificationAgent(BaseAgent):
    name = "Fact Verification Agent"
    description = "Removes duplicates, estimates confidence, and flags uncertain statements."

    def run(self, state: ResearchState) -> ResearchState:
        combined = state.search_results + state.rag_results
        if not combined:
            state.verified_facts = []
            state.confidence = 0.2
            return state

        # Local dedup by normalized sentence
        seen: set[str] = set()
        unique_sentences: list[str] = []
        for block in combined:
            for sentence in re.split(r"(?<=[.!?])\s+", block):
                s = sentence.strip()
                if len(s) < 20:
                    continue
                key = re.sub(r"\W+", "", s.lower())[:80]
                if key in seen:
                    continue
                seen.add(key)
                unique_sentences.append(s)

        # Ask the LLM to rate confidence and flag uncertainty markers
        sample = "\n".join(unique_sentences[:40])
        prompt = f"""You are a fact verification analyst. Given these research statements, estimate an overall confidence score
between 0 and 1 (1 = highly reliable) and identify any statements that are uncertain or speculative.
Return JSON: {{"confidence": float, "uncertain": [str, ...]}}

Statements:
{sample}
"""
        confidence = 0.7
        uncertain: list[str] = []
        try:
            import json
            raw = safe_invoke(prompt, temperature=0.1)
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                confidence = float(data.get("confidence", 0.7))
                uncertain = list(data.get("uncertain", []))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Verification parse failed: %s", exc)

        # Mark uncertain statements in the verified list
        flagged = []
        for s in unique_sentences:
            marker = ""
            for u in uncertain:
                if u.lower()[:30] in s.lower():
                    marker = " ⚠ (uncertain)"
                    break
            flagged.append(s + marker)

        state.verified_facts = flagged
        state.confidence = round(max(0.0, min(1.0, confidence)), 2)
        state.metadata["uncertain_statements"] = uncertain
        return state
