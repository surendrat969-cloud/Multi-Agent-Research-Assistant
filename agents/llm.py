"""Singleton Gemini LLM client used by all agents."""
from __future__ import annotations

import time
from functools import lru_cache
from typing import Optional

from config import settings
from utils.logger import logger

MAX_RETRIES = 3
RETRY_BASE_DELAY = 20  # seconds; Gemini free-tier retry hint is ~18-20s


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.4):
    """Build (and cache) the Gemini chat model via LangChain."""
    if not settings.is_configured:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add your key to the .env file "
            "(see .env.example). Get one at https://aistudio.google.com/apikey"
        )
    from langchain_google_genai import ChatGoogleGenerativeAI
    logger.info("Initializing Gemini model: %s", settings.gemini_model)
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
        max_output_tokens=8192,
    )


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "resource_exhausted" in msg or "429" in msg or "quota" in msg


def safe_invoke(prompt: str, temperature: float = 0.4) -> str:
    """Invoke the LLM and return text. Retries on rate-limit with backoff."""
    llm = get_llm(temperature)
    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = llm.invoke(prompt)
            text = getattr(resp, "content", str(resp))
            if isinstance(text, list):
                text = "".join(getattr(p, "text", str(p)) for p in text)
            return text.strip()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if _is_rate_limit(exc) and attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * attempt
                logger.warning("Rate limited (attempt %d/%d). Retrying in %ds…", attempt, MAX_RETRIES, delay)
                time.sleep(delay)
                continue
            logger.error("LLM invoke failed: %s", exc)
            raise
    raise RuntimeError(f"LLM invoke failed after {MAX_RETRIES} retries") from last_exc


def is_available() -> bool:
    return settings.is_configured
