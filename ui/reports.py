"""Reports library page: browse, search, open, rename, export saved reports."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from database import ReportRepository
from exports import export
from models.schemas import ReportRecord
from ui.components import apply_theme, hero
from ui.session import current_user


def reports_page() -> None:
    apply_theme()
    user = current_user()
    if not user:
        return
    hero("Reports Library", "Browse, search, and export your saved research reports.")

    selected_id = st.session_state.get("selected_report_id")

    if selected_id:
        rec = ReportRepository.get(selected_id)
        if rec:
            _render_detail(rec, user.id)
            if st.button("← Back to library"):
                st.session_state["selected_report_id"] = None
                st.rerun()
            return

    search = st.text_input("Search reports", key="lib_search")
    reports = ReportRepository.list_for_user(user.id, search=search)
    if not reports:
        st.info("No reports found. Run research from the Research page to create one.")
        return

    filter_opt = st.radio("Filter", ["All", "Bookmarks", "Favorites"], horizontal=True)
    if filter_opt == "Bookmarks":
        reports = [r for r in reports if r.bookmarked]
    elif filter_opt == "Favorites":
        reports = [r for r in reports if r.favorite]

    for r in reports:
        with st.container():
            cols = st.columns([5, 1, 1, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{r.title}**  \n_{r.query}_  \n{r.created_at[:10]} · ⏱ {r.duration_sec:.0f}s")
            with cols[1]:
                if st.button("Open", key=f"o_{r.id}"):
                    st.session_state["selected_report_id"] = r.id
                    st.rerun()
            with cols[2]:
                if st.button("Rename", key=f"rn_{r.id}"):
                    st.session_state[f"renaming_{r.id}"] = True
                    st.rerun()
            with cols[3]:
                if st.button("★", key=f"f_{r.id}"):
                    ReportRepository.update(r.id, favorite=not r.favorite)
                    st.rerun()
            with cols[4]:
                if st.button("🔖", key=f"b_{r.id}"):
                    ReportRepository.update(r.id, bookmarked=not r.bookmarked)
                    st.rerun()
            with cols[5]:
                if st.button("🗑", key=f"d_{r.id}"):
                    ReportRepository.delete(r.id)
                    st.rerun()

            if st.session_state.get(f"renaming_{r.id}"):
                new_title = st.text_input("New title", value=r.title, key=f"nt_{r.id}")
                if st.button("Save", key=f"sv_{r.id}"):
                    ReportRepository.update(r.id, title=new_title)
                    st.session_state[f"renaming_{r.id}"] = False
                    st.rerun()

            st.markdown('<div style="border-bottom:1px solid #334155; margin:.5rem 0"></div>', unsafe_allow_html=True)


def _render_detail(rec: ReportRecord, user_id: str) -> None:
    st.markdown(f"## {rec.title}")
    st.caption(f"Query: {rec.query} · {rec.created_at[:10]} · ⏱ {rec.duration_sec:.0f}s")
    st.markdown(rec.content)
    if rec.citations:
        st.markdown("### References")
        for c in rec.citations:
            st.markdown(c)
    st.markdown("---")
    fmt = st.selectbox("Export format", ["PDF", "DOCX", "Markdown", "TXT", "JSON"], key="detail_export_fmt")
    from models.schemas import ResearchState
    state = ResearchState(query=rec.query, citations=rec.citations,
                          improved_report=rec.content, keywords=rec.tags)
    if st.button("Export", key="detail_export_btn"):
        fname, data = export(state, fmt)
        st.download_button(f"Download {fname}", data=data, file_name=fname,
                           mime="application/octet-stream")
