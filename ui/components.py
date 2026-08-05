"""Streamlit UI theme, CSS, and shared components."""
from __future__ import annotations

import streamlit as st

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }

    .rm-hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f766e 100%);
        padding: 2rem 1.5rem; border-radius: 18px; color: white;
        margin-bottom: 1.2rem; box-shadow: 0 10px 30px rgba(15,23,42,0.35);
    }
    .rm-hero h1 { font-weight: 800; font-size: 2.2rem; margin: 0; }
    .rm-hero p { opacity: 0.92; margin-top: 0.5rem; }

    .rm-card {
        background: #1e293b; border-radius: 14px; padding: 1.1rem 1.2rem;
        border: 1px solid #334155; transition: transform .18s ease, box-shadow .18s ease;
    }
    .rm-card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(0,0,0,0.35); }

    .rm-stat {
        background: linear-gradient(135deg, #0f766e 0%, #1e3a8a 100%);
        border-radius: 14px; padding: 1.1rem; color: white; text-align: center;
    }
    .rm-stat .num { font-size: 1.8rem; font-weight: 800; }
    .rm-stat .lbl { font-size: .8rem; opacity: .9; text-transform: uppercase; letter-spacing: .05em; }

    .rm-badge {
        display:inline-block; padding:.25rem .6rem; border-radius:999px;
        font-size:.72rem; font-weight:600; background:#1e3a8a; color:#dbeafe;
    }
    .rm-badge.warn { background:#b45309; color:#fef3c7; }
    .rm-badge.ok { background:#15803d; color:#dcfce7; }

    .rm-agent-chip {
        display:inline-block; padding:.3rem .7rem; margin:.2rem; border-radius:8px;
        background:#334155; color:#e2e8f0; font-size:.78rem;
    }
    .rm-agent-chip.ok { background:#14532d; color:#bbf7d0; }
    .rm-agent-chip.err { background:#7f1d1d; color:#fecaca; }

    .rm-progress { height:8px; border-radius:6px; background:#334155; overflow:hidden; }
    .rm-progress > div { height:100%; background:linear-gradient(90deg,#2563eb,#14b8a6); }

    @keyframes rm-fade { from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:none;} }
    .rm-fade { animation: rm-fade .4s ease; }

    .rm-chat-user {
        background:#1e3a8a; color:#fff; padding:.7rem 1rem; border-radius:12px 12px 2px 12px;
        margin:.4rem 0 .4rem auto; max-width:80%; text-align:left;
    }
    .rm-chat-bot {
        background:#1e293b; color:#e2e8f0; padding:.7rem 1rem; border-radius:12px 12px 12px 2px;
        margin:.4rem 0; max-width:80%; border:1px solid #334155;
    }
</style>
"""


def apply_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="rm-hero rm-fade"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def stat_card(label: str, value) -> None:
    st.markdown(
        f'<div class="rm-stat rm-fade"><div class="num">{value}</div>'
        f'<div class="lbl">{label}</div></div>',
        unsafe_allow_html=True,
    )


def agent_chips(agent_log: list[dict]) -> None:
    chips = []
    for entry in agent_log:
        name = entry.get("agent", "?")
        status = entry.get("status", "?")
        cls = "ok" if status == "ok" else "err"
        chips.append(f'<span class="rm-agent-chip {cls}">{name} · {status}</span>')
    st.markdown("".join(chips), unsafe_allow_html=True)


def progress_bar(percent: float) -> None:
    st.markdown(
        f'<div class="rm-progress"><div style="width:{percent:.0f}%"></div></div>',
        unsafe_allow_html=True,
    )
