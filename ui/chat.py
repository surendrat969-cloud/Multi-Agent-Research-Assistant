"""AI Chat page with persistent conversation memory."""
from __future__ import annotations

import streamlit as st

from agents.llm import is_available, safe_invoke
from database import ChatRepository
from memory.conversation import ConversationMemory
from ui.components import apply_theme, hero
from ui.session import current_user
from utils.helpers import generate_id


def chat_page() -> None:
    apply_theme()
    user = current_user()
    if not user:
        return
    hero("AI Chat", "Ask follow-up questions with persistent conversation memory.")

    if not is_available():
        st.warning("Add your Gemini API key to the `.env` file to use the chat.")
        return

    # Session selection
    sessions = ChatRepository.sessions(user.id)
    c_left, c_right = st.columns([4, 1])
    with c_left:
        options = ["New conversation"] + [s["session_id"] for s in sessions]
        labels = ["New conversation"] + [
            f"{s.get('topic','Conversation')[:40]} ({s.get('last','')[:10]})" for s in sessions
        ]
        choice = st.selectbox("Conversation", options, format_func=lambda x: dict(zip(options, labels))[x])
    with c_right:
        if st.button("New", use_container_width=True):
            st.session_state["chat_session_id"] = None
            st.rerun()

    if choice == "New conversation" or st.session_state.get("chat_session_id") is None:
        st.session_state["chat_session_id"] = generate_id("chat")

    session_id = st.session_state["chat_session_id"]
    memory = ConversationMemory(user.id, session_id).load()

    # Render history
    for msg in memory.messages():
        cls = "rm-chat-user" if msg.role == "user" else "rm-chat-bot"
        st.markdown(f'<div class="{cls} rm-fade">{msg.content}</div>', unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Message", height=100, key="chat_input")
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            submitted = st.form_submit_button("Send", type="primary", use_container_width=True)
        with c2:
            regenerate = st.form_submit_button("Regenerate", use_container_width=True)
        with c3:
            export_btn = st.form_submit_button("Export", use_container_width=True)

    if submitted and user_input.strip():
        memory.add_user(user_input.strip())
        context = memory.as_prompt_context()
        prompt = f"""You are ResearchMind AI, a helpful research assistant. Use the conversation context to answer.

Conversation so far:
{context}

User: {user_input}
Assistant:"""
        try:
            answer = safe_invoke(prompt, temperature=0.4)
        except Exception as exc:  # noqa: BLE001
            answer = f"Sorry, I couldn't generate a response: {exc}"
        memory.add_assistant(answer)
        st.rerun()

    if regenerate:
        last_user = next((m for m in reversed(memory.messages()) if m.role == "user"), None)
        if last_user:
            try:
                answer = safe_invoke(
                    f"Re-answer this research question more thoroughly:\n{last_user.content}",
                    temperature=0.6,
                )
            except Exception as exc:  # noqa: BLE001
                answer = f"Regeneration failed: {exc}"
            memory.add_assistant(answer)
            st.rerun()

    if export_btn and memory.messages():
        export_text = "\n\n".join(f"{m.role.capitalize()}: {m.content}" for m in memory.messages())
        st.download_button(
            "Download chat (.txt)",
            data=export_text.encode("utf-8"),
            file_name=f"chat_{session_id}.txt",
            mime="text/plain",
        )
