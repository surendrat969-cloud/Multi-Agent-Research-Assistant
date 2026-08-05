"""Dashboard page: stats, charts, research history."""
from __future__ import annotations

from collections import Counter
from typing import Optional

import streamlit as st

from database import ChatRepository, ReportRepository
from services.visualization import reports_over_time_chart, topics_bar_chart
from ui.components import apply_theme, hero, stat_card
from ui.session import current_user


def dashboard_page() -> None:
    apply_theme()
    user = current_user()
    if not user:
        return
    hero("Dashboard", f"Welcome back, {user.username}. Here's your research activity.")

    reports = ReportRepository.list_for_user(user.id)
    chat_sessions = ChatRepository.sessions(user.id)

    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Total Reports", len(reports))
    with c2:
        stat_card("Chat Sessions", len(chat_sessions))
    avg_time = (sum(r.duration_sec for r in reports) / len(reports)) if reports else 0
    with c3:
        stat_card("Avg Research Time", f"{avg_time:.0f}s")
    with c4:
        stat_card("Bookmarks", sum(1 for r in reports if r.bookmarked))

    st.markdown("---")

    # Charts
    left, right = st.columns(2)
    with left:
        dates = [r.created_at[:10] for r in reports]
        st.plotly_chart(reports_over_time_chart(dates), use_container_width=True)
    with right:
        topic_counter: Counter = Counter()
        for r in reports:
            for kw in (r.tags or [r.query]):
                topic_counter[kw] += 1
        topics = topic_counter.most_common(8)
        st.plotly_chart(topics_bar_chart(topics), use_container_width=True)

    # Research history
    st.markdown("### Research History")
    if not reports:
        st.info("No reports yet. Start a research query to see your history here.")
        return
    search = st.text_input("Search reports", key="dash_search")
    filtered = ReportRepository.list_for_user(user.id, search=search) if search else reports
    for r in filtered:
        with st.container():
            cols = st.columns([6, 1, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**{r.title}**  \n_{r.query}_  \n{r.created_at[:10]} · ⏱ {r.duration_sec:.0f}s")
            with cols[1]:
                if st.button("Open", key=f"open_{r.id}"):
                    st.session_state["selected_report_id"] = r.id
                    st.session_state["page"] = "Reports"
                    st.rerun()
            with cols[2]:
                if st.button("★", key=f"fav_{r.id}", help="Toggle favorite"):
                    ReportRepository.update(r.id, favorite=not r.favorite)
                    st.rerun()
            with cols[3]:
                if st.button("🔖", key=f"bm_{r.id}", help="Toggle bookmark"):
                    ReportRepository.update(r.id, bookmarked=not r.bookmarked)
                    st.rerun()
            with cols[4]:
                if st.button("🗑", key=f"del_{r.id}", help="Delete"):
                    ReportRepository.delete(r.id)
                    st.rerun()
            st.markdown('<div style="border-bottom:1px solid #334155; margin:.5rem 0"></div>', unsafe_allow_html=True)
