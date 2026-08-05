"""ResearchMind AI – main Streamlit entry point."""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database import init_db
from ui.auth import auth_page, profile_page
from ui.chat import chat_page
from ui.components import apply_theme
from ui.dashboard import dashboard_page
from ui.reports import reports_page
from ui.research import research_page
from ui.session import current_user, init_session_state, is_authenticated, logout

init_db()
init_session_state()
apply_theme()


def sidebar_nav() -> None:
    with st.sidebar:
        st.markdown("## 🧠 ResearchMind AI")
        st.caption("Multi-Agent Research Assistant")

        if is_authenticated():
            user = current_user()
            st.markdown(f"**Signed in as**  \n{user.username}")
            pages = ["Dashboard", "Research", "AI Chat", "Reports", "Profile"]
            choice = st.radio("Navigate", pages, label_visibility="collapsed")
            st.session_state["page"] = choice
            st.markdown("---")
            if st.button("Log out", use_container_width=True):
                logout()
                st.rerun()
            st.markdown("---")
            st.caption("Powered by Google Gemini 2.5 Flash · LangGraph · FAISS")
        else:
            st.info("Sign in to access the full workspace.")


def main() -> None:
    sidebar_nav()

    if not is_authenticated():
        auth_page()
        return

    page = st.session_state.get("page", "Dashboard")
    if page == "Dashboard":
        dashboard_page()
    elif page == "Research":
        research_page()
    elif page == "AI Chat":
        chat_page()
    elif page == "Reports":
        reports_page()
    elif page == "Profile":
        profile_page()


if __name__ == "__main__":
    main()
