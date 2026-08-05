"""LangGraph orchestration: chains the 10 agents into a research pipeline."""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents.base import BaseAgent
from agents.citation import CitationAgent
from agents.critic import CriticAgent
from agents.enrichment import EnrichmentAgent
from agents.fact_verification import FactVerificationAgent
from agents.interview import InterviewAgent
from agents.planner import PlannerAgent
from agents.presentation import PresentationAgent
from agents.quiz import QuizAgent
from agents.rag import RAGAgent
from agents.search import SearchAgent
from agents.writer import WriterAgent
from models.schemas import ResearchState
from utils.logger import logger


class GraphState(TypedDict, total=False):
    state: ResearchState


class ResearchPipeline:
    """Runs all agents sequentially via LangGraph."""

    def __init__(self) -> None:
        self.agents: list[BaseAgent] = [
            PlannerAgent(),
            SearchAgent(),
            RAGAgent(),
            FactVerificationAgent(),
            WriterAgent(),
            CriticAgent(),
            EnrichmentAgent(),
            CitationAgent(),
            PresentationAgent(),
            InterviewAgent(),
            QuizAgent(),
        ]
        self.graph = self._build_graph()

    def _wrap(self, agent: BaseAgent):
        def fn(gs: GraphState) -> GraphState:
            state = gs.get("state")
            if state is None:
                raise ValueError("Pipeline state is missing")
            new_state = agent.execute(state)
            return {"state": new_state}
        return fn

    def _build_graph(self):
        g = StateGraph(GraphState)
        prev = None
        for i, agent in enumerate(self.agents):
            node_name = f"node_{i}_{agent.name.replace(' ', '_').lower()}"
            g.add_node(node_name, self._wrap(agent))
            if prev:
                g.add_edge(prev, node_name)
            else:
                g.set_entry_point(node_name)
            prev = node_name
        g.add_edge(prev, END)
        return g.compile()

    def run(self, query: str) -> ResearchState:
        state = ResearchState(query=query)
        logger.info("Pipeline started for query: %s", query)
        result = self.graph.invoke({"state": state})
        final = result["state"]
        logger.info(
            "Pipeline finished. Agents run: %d, errors: %d",
            len(final.agent_log), len(final.errors),
        )
        return final


pipeline = ResearchPipeline()
