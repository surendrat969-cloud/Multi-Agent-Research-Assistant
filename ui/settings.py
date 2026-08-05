"""Settings page — allow entering the Gemini API key from the web UI."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import settings as cfg
from config.settings import reload_settings


def _write_env_var(key: str, value: str) -> None:
    p = Path(".env")
    lines: list[str] = []
    if p.exists():
        lines = p.read_text(encoding="utf-8").splitlines()

    for i, ln in enumerate(lines):
        if ln.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")

    p.write_text("\n".join(lines), encoding="utf-8")


def settings_page() -> None:
    st.title("Settings")
    st.caption("Manage runtime configuration")

    cur = cfg.gemini_api_key or ""
    api = st.text_input("Gemini API key", value=cur, type="password")

    if st.button("Save API key"):
        if not api.strip():
            st.error("API key cannot be empty")
            return
        _write_env_var("GEMINI_API_KEY", api.strip())
        # reload settings into the running process
        reload_settings()
        st.success("Saved GEMINI_API_KEY to .env and reloaded settings.")
        st.info("The app will rerun to apply new configuration.")
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
