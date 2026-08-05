"""Session state helpers for auth and navigation."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from models.schemas import User


def init_session_state() -> None:
    defaults = {
        "user": None,  # User | None
        "page": "Dashboard",
        "chat_session_id": None,
        "last_state": None,
        "research_running": False,
        "theme": "dark",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def current_user() -> Optional[User]:
    return st.session_state.get("user")


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


def set_user(user: Optional[User]) -> None:
    st.session_state["user"] = user


def logout() -> None:
    st.session_state["user"] = None
    st.session_state["chat_session_id"] = None
    st.session_state["last_state"] = None
