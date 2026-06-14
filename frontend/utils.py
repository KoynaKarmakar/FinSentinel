"""Shared utilities — CSS injection, sidebar, backend URL."""
import math
import os

import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")


# ── CSS ───────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
/* ── Hide Streamlit chrome ───────────────────────── */
#MainMenu          { visibility: hidden; }
footer             { visibility: hidden; }
header             { visibility: hidden; }
.stDeployButton    { display: none; }
[data-testid="stSidebarNav"]      { display: none !important; }
[data-testid="stSidebarNavItems"] { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }

/* ── App background ──────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #020B18 0%, #041020 60%, #020B18 100%) !important;
}
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

/* ── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #06111F !important;
    border-right: 1px solid rgba(30, 144, 255, 0.12) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
}

/* ── Page-link styling ───────────────────────────── */
[data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.55) !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: background 0.15s, color 0.15s !important;
    margin-bottom: 2px !important;
}
[data-testid="stPageLink"] a:hover {
    background: rgba(30, 144, 255, 0.1) !important;
    color: #FFFFFF !important;
}
[data-testid="stPageLink"][aria-current="page"] a {
    background: rgba(30, 144, 255, 0.15) !important;
    color: #60AFFF !important;
}

/* ── Text colours ────────────────────────────────── */
h1, h2, h3, h4 { color: #FFFFFF !important; }
p, li, .stMarkdown { color: rgba(255,255,255,0.75) !important; }
label { color: rgba(255,255,255,0.65) !important; }

/* ── Inputs ──────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(30,144,255,0.2) !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
}
.stCheckbox label { color: rgba(255,255,255,0.7) !important; }

/* ── Buttons ─────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1E6FCC, #1E90FF) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    transition: opacity 0.15s !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }
.stButton > button[kind="secondary"] {
    background: rgba(30,144,255,0.08) !important;
    border: 1px solid rgba(30,144,255,0.25) !important;
    border-radius: 8px !important;
    color: #60AFFF !important;
    font-weight: 500 !important;
}

/* ── Expanders ───────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(30,144,255,0.12) !important;
    border-radius: 8px !important;
}

/* ── Metrics ─────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(30,144,255,0.12) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.5) !important; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; }

/* ── Dataframe ───────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 8px !important; }

/* ── Alerts ──────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Divider ─────────────────────────────────────── */
hr { border-color: rgba(30,144,255,0.12) !important; }

/* ── File uploader ───────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(30,144,255,0.25) !important;
    border-radius: 10px !important;
}

/* ── Download button ─────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #0F4F1E, #1A8C36) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ── Status widget ───────────────────────────────── */
[data-testid="stStatusWidget"] { border-radius: 8px !important; }
</style>
"""


def inject_global_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    inject_global_css()
    with st.sidebar:
        # Logo block
        st.markdown(
            """
            <div style="
                display:flex; align-items:center; gap:10px;
                padding:0.25rem 0.5rem 1rem;
            ">
                <div style="
                    width:38px; height:38px; border-radius:10px; flex-shrink:0;
                    background:linear-gradient(135deg,#1E90FF,#0050CC);
                    display:flex; align-items:center; justify-content:center;
                    font-size:18px; box-shadow:0 4px 14px rgba(30,144,255,0.4);
                ">🔍</div>
                <div>
                    <div style="font-size:15px;font-weight:700;color:#FFFFFF;letter-spacing:-0.3px;line-height:1.1">
                        FinSentinel
                    </div>
                    <div style="font-size:10.5px;color:rgba(255,255,255,0.35);margin-top:1px">
                        Compliance AI
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='height:1px;background:rgba(30,144,255,0.12);margin:0 0.5rem 1rem;'></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='font-size:10px;font-weight:600;color:rgba(255,255,255,0.28);"
            "letter-spacing:1.6px;padding:0 0.5rem;margin-bottom:6px;'>NAVIGATION</div>",
            unsafe_allow_html=True,
        )

        st.page_link("app.py",                    label="Home",           icon="🏠")
        st.page_link("pages/1_knowledge_base.py", label="Knowledge Base", icon="📄")
        st.page_link("pages/2_investigate.py",    label="Investigate",    icon="🔎")

        st.markdown(
            "<div style='height:1px;background:rgba(30,144,255,0.12);margin:1rem 0.5rem 0.75rem;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-size:10px;color:rgba(255,255,255,0.22);padding:0 0.5rem'>"
            "v1.0.0 · Groq · LangGraph · Qdrant</div>",
            unsafe_allow_html=True,
        )


# ── Score helpers ─────────────────────────────────────────────────────────────

def logit_to_confidence(score: float) -> float:
    """Maps logs linearly between a logical worst-case and best-case window."""
    min_logit = -3.0  # Becomes 0%
    max_logit = 3.0   # Becomes 100%
    
    # Linear interpolation formula
    percentage = ((score - min_logit) / (max_logit - min_logit)) * 100
    
    # Keep it tightly locked between 0 and 100
    return round(max(0.0, min(100.0, percentage)), 1)


def confidence_bar_html(confidence: float, label: str = "") -> str:
    """Returns an HTML confidence bar string."""
    if confidence >= 80:
        colour = "#1E90FF"
    elif confidence >= 50:
        colour = "#F0A500"
    else:
        colour = "#888880"
    return (
        f"<div style='margin:4px 0 8px;'>"
        f"<div style='display:flex;justify-content:space-between;margin-bottom:3px;'>"
        f"<span style='font-size:11px;color:rgba(255,255,255,0.4);'>{label}</span>"
        f"<span style='font-size:12px;font-weight:600;color:{colour};'>{confidence:.1f}%</span>"
        f"</div>"
        f"<div style='height:5px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;'>"
        f"<div style='height:100%;width:{confidence}%;background:{colour};"
        f"border-radius:3px;transition:width 0.6s ease;'></div>"
        f"</div>"
        f"</div>"
    )
