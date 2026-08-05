"""Research page: run the multi-agent pipeline, view results and exports."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from agents.llm import is_available
from exports import export
from models.schemas import ResearchState
from services.research_service import FileService, ResearchService
from ui.components import agent_chips, apply_theme, hero, progress_bar
from ui.session import current_user


def _render_enrichment(state: ResearchState) -> None:
    enrich = state.metadata.get("enrichment", {})
    if not enrich:
        return

    tabs = st.tabs([
        "Summary", "FAQ", "Glossary", "SWOT", "Resources",
        "Timeline", "Formulas", "Applications",
    ])
    with tabs[0]:
        st.markdown(f"**Abstract:** {enrich.get('abstract','')}")
        st.markdown(f"**Executive Summary:** {enrich.get('summary','')}")
        if state.keywords:
            st.markdown("**Keywords:** " + ", ".join(f"`{k}`" for k in state.keywords))
    with tabs[1]:
        faq = enrich.get("faq", [])
        if faq:
            for i, item in enumerate(faq, 1):
                with st.expander(f"Q{i}: {item.get('question','')}"):
                    st.markdown(item.get("answer", ""))
        else:
            st.info("No FAQ generated.")
    with tabs[2]:
        glossary = enrich.get("glossary", [])
        if glossary:
            for g in glossary:
                st.markdown(f"**{g.get('term','')}** — {g.get('definition','')}")
        else:
            st.info("No glossary terms.")
    with tabs[3]:
        swot = enrich.get("swot", {})
        if swot:
            from services.visualization import swot_radar
            st.plotly_chart(swot_radar(swot), use_container_width=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Strengths:**")
                for s in swot.get("strengths", []):
                    st.markdown(f"- {s}")
                st.markdown("**Weaknesses:**")
                for w in swot.get("weaknesses", []):
                    st.markdown(f"- {w}")
            with c2:
                st.markdown("**Opportunities:**")
                for o in swot.get("opportunities", []):
                    st.markdown(f"- {o}")
                st.markdown("**Threats:**")
                for t in swot.get("threats", []):
                    st.markdown(f"- {t}")
        else:
            st.info("No SWOT analysis.")
    with tabs[4]:
        for label, key in [("Learning Resources", "learning_resources"),
                           ("GitHub", "github_resources"),
                           ("YouTube", "youtube_resources"),
                           ("Books", "books"),
                           ("Research Papers", "papers")]:
            items = enrich.get(key, [])
            if items:
                st.markdown(f"**{label}**")
                for it in items:
                    if isinstance(it, dict):
                        title = it.get("title", "")
                        extra = it.get("url") or it.get("author") or it.get("authors", "")
                        st.markdown(f"- {title} — {extra}")
                    else:
                        st.markdown(f"- {it}")
    with tabs[5]:
        timeline = enrich.get("timeline", [])
        if timeline:
            from services.visualization import mermaid_timeline
            st.markdown(f"```mermaid\n{mermaid_timeline(timeline)}\n```")
            for t in timeline:
                st.markdown(f"- **{t.get('year','')}**: {t.get('event','')}")
        else:
            st.info("No timeline available.")
    with tabs[6]:
        formulas = enrich.get("formulas", [])
        if formulas:
            for f in formulas:
                st.markdown(f"**{f.get('name','')}**: `{f.get('formula','')}`")
        else:
            st.info("No specific formulas identified for this topic.")
    with tabs[7]:
        apps = enrich.get("applications", [])
        if apps:
            for a in apps:
                st.markdown(f"- {a}")
        else:
            st.info("No applications listed.")


def research_page() -> None:
    apply_theme()
    user = current_user()
    if not user:
        return
    hero("Research Workspace", "Enter any topic and let the multi-agent pipeline do the rest.")

    if not is_available():
        st.warning(
            "Add your Google Gemini API key to the `.env` file "
            "(see `.env.example`). Get one at https://aistudio.google.com/apikey"
        )
        return

    # File upload
    with st.expander("Upload documents (PDF / DOCX / TXT) for RAG", expanded=False):
        uploaded = st.file_uploader(
            "Drag and drop files here",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )
        if uploaded and st.button("Process uploads", use_container_width=False):
            count = 0
            for f in uploaded:
                rec = FileService.process_upload(f, user.id)
                if rec:
                    count += 1
            if count:
                st.success(f"Indexed {count} file(s) into the knowledge base.")
            else:
                st.warning("No readable text found in the uploaded files.")

    # Query input
    query = st.text_input("Research topic", placeholder="e.g., Transformer architectures in NLP",
                          key="research_query")

    col_run, col_clear = st.columns([3, 1])
    with col_run:
        run_btn = st.button("Run Research", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state["last_state"] = None
            st.rerun()

    if run_btn and query.strip():
        progress = st.progress(0, text="Running multi-agent pipeline…")
        try:
            service = ResearchService()
            for pct in range(0, 101, 10):
                progress.progress(pct, text="Agents working…")
            result_state = service.run(user.id, query.strip())
            progress.progress(100, text="Done!")
            st.session_state["last_state"] = result_state
            st.success("Research complete!")
        except Exception as exc:  # noqa: BLE001
            progress.empty()
            st.error(f"Research failed: {exc}")
            return

    state: Optional[ResearchState] = st.session_state.get("last_state")
    if not state:
        st.info("Run a research query to see the full report, citations, slides, quiz, and more.")
        return

    # Agent execution log
    st.markdown("### Agent Execution")
    agent_chips(state.agent_log)
    st.caption(f"Confidence: **{state.confidence:.0%}** · "
               f"Difficulty: **{state.metadata.get('difficulty','—')}** · "
               f"Reading time: ~{state.metadata.get('reading_time_min','—')} min · "
               f"Quality score: {state.metadata.get('quality_score','—')}")

    # Tabs for outputs
    tabs = st.tabs([
        "Report", "Citations", "Slides", "Interview", "Quiz", "Enrichment", "Diagrams", "Export",
    ])

    with tabs[0]:
        st.markdown(state.improved_report or state.report)
    with tabs[1]:
        for c in state.citations:
            st.markdown(c)
    with tabs[2]:
        for i, slide in enumerate(state.slides, 1):
            st.markdown(f"**Slide {i}: {slide.get('title','')}**")
            for b in slide.get("bullets", []):
                st.markdown(f"- {b}")
    with tabs[3]:
        for i, item in enumerate(state.interview, 1):
            with st.expander(f"Q{i}: {item.get('question','')}"):
                st.markdown(item.get("answer", ""))
    with tabs[4]:
        for i, q in enumerate(state.quiz, 1):
            st.markdown(f"**Q{i}.** {q.get('question','')}")
            for j, opt in enumerate(q.get("options", [])):
                st.markdown(f"  - {'ABCD'[j]}. {opt}")
            st.markdown(f"  *Answer:* {'ABCD'[q.get('answer',0)]}")
            st.markdown("---")
    with tabs[5]:
        _render_enrichment(state)
    with tabs[6]:
        from services.visualization import mermaid_flowchart, mermaid_mindmap
        st.markdown("**Pipeline Flowchart**")
        st.markdown(f"```mermaid\n{mermaid_flowchart(state.query)}\n```")
        st.markdown("**Mind Map**")
        st.markdown(f"```mermaid\n{mermaid_mindmap(state.query, state.keywords)}\n```")
    with tabs[7]:
        fmt = st.selectbox("Format", ["PDF", "DOCX", "Markdown", "TXT", "JSON"])
        if st.button("Download", type="primary"):
            fname, data = export(state, fmt)
            st.download_button(
                label=f"Download {fname}",
                data=data,
                file_name=fname,
                mime="application/octet-stream",
            )
