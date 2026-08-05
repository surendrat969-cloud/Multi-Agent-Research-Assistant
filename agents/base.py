"""Base class for all agents: uniform logging, error capture, token tracking."""
from __future__ import annotations

import time
from typing import Any, ClassVar

from models.schemas import ResearchState
from utils.helpers import log_execution
from utils.logger import logger


class BaseAgent:
    """Subclasses implement `run(state) -> ResearchState`."""

    name: ClassVar[str] = "BaseAgent"
    description: ClassVar[str] = ""

    @log_execution("BaseAgent")
    def execute(self, state: ResearchState) -> ResearchState:
        start = time.perf_counter()
        try:
            result = self.run(state)
            elapsed = time.perf_counter() - start
            result.agent_log.append(
                {
                    "agent": self.name,
                    "status": "ok",
                    "duration_sec": round(elapsed, 3),
                }
            )
            return result
        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - start
            logger.error("%s error: %s", self.name, exc)
            state.errors.append(f"{self.name}: {exc}")
            state.agent_log.append(
                {
                    "agent": self.name,
                    "status": "error",
                    "duration_sec": round(elapsed, 3),
                    "error": str(exc),
                }
            )
            return state

    def run(self, state: ResearchState) -> ResearchState:  # pragma: no cover
        raise NotImplementedError
