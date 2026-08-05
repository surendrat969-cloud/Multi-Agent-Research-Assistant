"""RAG Agent: retrieves knowledge from uploaded documents via FAISS."""
from __future__ import annotations

from agents.base import BaseAgent
from models.schemas import ResearchState
from rag.vector_store import store
from utils.helpers import truncate
from utils.logger import logger


class RAGAgent(BaseAgent):
    name = "RAG Agent"
    description = "Retrieves relevant knowledge from uploaded documents using vector search."

    def run(self, state: ResearchState) -> ResearchState:
        if store.size == 0:
            logger.info("RAG Agent: no documents indexed, skipping retrieval")
            return state
        results: list[str] = []
        for task in state.tasks:
            if task.source == "web":
                continue
            hits = store.search(task.description, k=4)
            if hits:
                joined = "\n\n".join(truncate(h, 1200) for h in hits)
                results.append(f"## {task.description}\n[From uploaded documents]\n{joined}")
        state.rag_results = results
        return state
