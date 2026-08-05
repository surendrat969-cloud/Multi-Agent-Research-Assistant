"""Authentication UI: login, signup, forgot password."""
from __future__ import annotations

import streamlit as st

from services.auth_service import AuthService
from ui.components import apply_theme, hero
from ui.session import set_user


def auth_page() -> None:
    apply_theme()
    hero("ResearchMind AI", "Multi-Agent Research Assistant — sign in to begin.")
    tab_login, tab_signup, tab_forgot = st.tabs(["Login", "Sign Up", "Forgot Password"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
            if submitted:
                ok, msg, user = AuthService.login(username.strip(), password)
                if ok and user:
                    set_user(user)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_signup:
        with st.form("signup_form", clear_on_submit=False):
            username = st.text_input("Choose a username")
            email = st.text_input("Email")
            password = st.text_input("Password (min 6 chars)", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg, user = AuthService.signup(username.strip(), email.strip(), password)
                    if ok and user:
                        set_user(user)
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_forgot:
        with st.form("forgot_form", clear_on_submit=False):
            email = st.text_input("Account email")
            new_password = st.text_input("New password (min 6 chars)", type="password")
            submitted = st.form_submit_button("Reset Password", use_container_width=True)
            if submitted:
                ok, msg = AuthService.reset_password(email.strip(), new_password)
                if ok:
                    st.success(msg + " You can now log in.")
                else:
                    st.error(msg)


def profile_page() -> None:
    from database import ReportRepository
    from ui.components import stat_card
    from ui.session import current_user

    user = current_user()
    if not user:
        return
    apply_theme()
    st.markdown(f"## Profile — {user.username}")
    st.markdown(f"**Email:** {user.email}")
    st.markdown(f"**Member since:** {user.created_at[:10]}")
    reports = ReportRepository.list_for_user(user.id)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Total Reports", len(reports))
    with c2:
        stat_card("Bookmarks", sum(1 for r in reports if r.bookmarked))
    with c3:
        stat_card("Favorites", sum(1 for r in reports if r.favorite))
