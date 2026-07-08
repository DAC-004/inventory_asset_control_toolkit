"""Enterprise theme and custom CSS for Streamlit."""

import streamlit as st

COLORS = {
    "primary": "#1E3A5F",
    "secondary": "#2563EB",
    "accent": "#0EA5E9",
    "background": "#F8FAFC",
    "surface": "#FFFFFF",
    "text": "#0F172A",
    "muted": "#64748B",
    "success": "#059669",
    "warning": "#D97706",
    "danger": "#DC2626",
    "border": "#E2E8F0",
}

PLOTLY_TEMPLATE = "plotly_white"

_COMPACT_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

section[data-testid="stMain"] div[data-testid="stMainBlockContainer"],
section.main .block-container,
.block-container {{
    padding-top: 0.35rem !important;
    padding-bottom: 1.25rem !important;
    max-width: 1400px;
}}

header[data-testid="stHeader"] {{
    height: 2.5rem !important;
    background: transparent !important;
}}

section[data-testid="stSidebar"] {{
    background-color: #F8FAFC;
}}

section[data-testid="stSidebar"] > div {{
    padding-top: 0.5rem !important;
}}

section[data-testid="stSidebar"] .nav-section-title {{
    color: {COLORS["muted"]};
    font-size: 0.65rem !important;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 0.5rem 0.1rem !important;
    line-height: 1.3;
}}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
    gap: 0.4rem !important;
}}

section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] button[kind="primary"],
section[data-testid="stSidebar"] button[kind="secondary"] {{
    justify-content: flex-start !important;
    text-align: left !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    line-height: 1.3 !important;
    border-radius: 5px !important;
    padding: 0.45rem 0.7rem !important;
    min-height: 2rem !important;
    height: auto !important;
    margin-bottom: 0.1rem !important;
    box-shadow: none !important;
    white-space: normal !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: transparent !important;
    border: 1px solid transparent !important;
    color: #475569 !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background-color: #F1F5F9 !important;
    border-color: #E2E8F0 !important;
    color: {COLORS["primary"]} !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] button[kind="primary"] {{
    background-color: #EFF6FF !important;
    border: 1px solid #DBEAFE !important;
    border-left: 3px solid {COLORS["secondary"]} !important;
    color: {COLORS["primary"]} !important;
    font-weight: 600 !important;
}}

section[data-testid="stSidebar"] hr {{
    margin: 0.75rem 0 !important;
}}

section[data-testid="stSidebar"] h4, section[data-testid="stSidebar"] h5 {{
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    margin: 0.35rem 0 0.5rem 0 !important;
    line-height: 1.3 !important;
    color: {COLORS["text"]} !important;
}}

.sidebar-section {{
    margin-top: 0.25rem;
}}

.sidebar-metric {{
    font-size: 0.78rem !important;
    color: {COLORS["muted"]} !important;
    margin: 0 0 0.35rem 0 !important;
    line-height: 1.45 !important;
    display: block;
    word-break: break-word;
}}

.kpi-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 0.9rem 1rem;
    min-height: 118px;
    height: 100%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
}}

.kpi-label {{
    color: {COLORS["muted"]};
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    line-height: 1.3;
    margin-bottom: 0.15rem;
}}

.kpi-value {{
    color: {COLORS["text"]};
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0.1rem 0 0.35rem 0;
    line-height: 1.2;
}}

.kpi-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-top: auto;
    flex-wrap: wrap;
}}

.kpi-context {{
    color: {COLORS["muted"]};
    font-size: 0.75rem;
    line-height: 1.3;
    flex: 1;
    min-width: 0;
}}

.status-badge {{
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
}}

.badge-high {{ background: #FEE2E2; color: #991B1B; }}
.badge-medium {{ background: #FEF3C7; color: #92400E; }}
.badge-low {{ background: #D1FAE5; color: #065F46; }}
.badge-neutral {{ background: #DBEAFE; color: #1E40AF; }}

.panel-box {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}}

.stDownloadButton button {{
    border-radius: 8px;
}}

h3 {{
    margin-top: 0.25rem !important;
    margin-bottom: 0.35rem !important;
    font-size: 1.15rem !important;
}}

[data-testid="stCaptionContainer"] {{
    margin-bottom: 0.75rem !important;
}}

[data-testid="stCaptionContainer"] p {{
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
}}
</style>
"""


def apply_theme() -> None:
    st.markdown(_COMPACT_CSS, unsafe_allow_html=True)


def apply_sidebar_theme() -> None:
    st.markdown(_COMPACT_CSS, unsafe_allow_html=True)
