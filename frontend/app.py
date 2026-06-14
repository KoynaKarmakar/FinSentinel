import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import render_sidebar

st.set_page_config(
    page_title="FinSentinel — Compliance AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_sidebar()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 3.5rem 2rem 1rem; text-align: center; max-width: 860px; margin: 0 auto;">
    <div style="
        display: inline-flex; align-items: center; gap: 8px;
        background: rgba(30,144,255,0.1);
        border: 1px solid rgba(30,144,255,0.3);
        border-radius: 20px; padding: 5px 16px;
        font-size: 11.5px; color: #60AFFF; font-weight: 500;
        margin-bottom: 1.5rem;
    ">
        ⚡ Agentic AI &nbsp;·&nbsp; RegTech &nbsp;·&nbsp; LangGraph &nbsp;·&nbsp; Hybrid RAG
    </div>
    <h1 style="
        font-size: clamp(2.2rem, 5vw, 3.6rem);
        font-weight: 800; line-height: 1.08;
        color: #FFFFFF; letter-spacing: -0.5px; margin-bottom: 1.1rem;
    ">
        Compliance Investigation,<br>
        <span style="
            background: linear-gradient(135deg, #60AFFF 0%, #1E90FF 50%, #0055DD 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        ">Automated.</span>
    </h1>
    <p style="
        font-size: 1.05rem; color: rgba(255,255,255,0.5);
        max-width: 580px; margin: 0 auto 2.5rem; line-height: 1.7;
    ">
        Submit a suspicious transaction. Receive a cited, explainable investigation report
        grounded in RBI, PMLA, FATF, and FIU-IND regulations — in under 30 seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# CTA buttons
col_l, c1, c2, col_r = st.columns([2.5, 1, 1, 2.5])
with c1:
    if st.button("▶  Start Investigating", type="primary", use_container_width=True):
        st.switch_page("pages/2_investigate.py")
with c2:
    if st.button("📄  Upload Docs", type="secondary", use_container_width=True):
        st.switch_page("pages/1_knowledge_base.py")

# ── Glowing Orb + Agent Cards ─────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes pulse-orb {
    0%,100% {
        box-shadow: 0 0 70px 25px rgba(30,144,255,0.35),
                    0 0 140px 50px rgba(20,80,200,0.18),
                    inset 0 0 40px rgba(100,180,255,0.15);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 90px 35px rgba(30,144,255,0.5),
                    0 0 180px 70px rgba(20,80,200,0.28),
                    inset 0 0 60px rgba(100,180,255,0.2);
        transform: scale(1.04);
    }
}
@keyframes spin-ring {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes fade-in-card {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.orb-scene {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem 0 1rem;
    min-height: 240px;
}
.orb {
    width: 150px; height: 150px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%,
        #5AB4FF 0%, #1E70DD 30%, #0A3A80 65%, #040D21 100%);
    animation: pulse-orb 4s ease-in-out infinite;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.8rem; position: relative; z-index: 3;
}
.orb-ring {
    position: absolute; border-radius: 50%;
    border: 1px solid rgba(30,144,255,0.2);
    z-index: 2;
}
.ring-1 { width:190px;height:190px; animation: spin-ring 12s linear infinite; border-color: rgba(30,144,255,0.3); border-style: dashed; }
.ring-2 { width:230px;height:230px; animation: spin-ring 20s linear infinite reverse; }
.line-left, .line-right {
    position: absolute; top: 50%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(30,144,255,0.4), transparent);
    width: 120px; z-index: 1;
}
.line-left  { right: calc(50% + 115px); }
.line-right { left: calc(50% + 115px); }
</style>

<div class="orb-scene">
    <div class="orb-ring ring-2"></div>
    <div class="orb-ring ring-1"></div>
    <div class="orb">🔍</div>
    <div class="line-left"></div>
    <div class="line-right"></div>
</div>
""", unsafe_allow_html=True)

# ── Agent Cards ───────────────────────────────────────────────────────────────
st.markdown("<div style='max-width:920px;margin:0 auto;padding:0 1rem 3rem;'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="medium")

CARD_CSS = """
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(30,144,255,0.14);
    border-radius: 14px;
    padding: 1.5rem;
    height: 100%;
    transition: border-color 0.2s;
"""

with col1:
    st.markdown(f"""
    <div style="{CARD_CSS}">
        <div style="font-size:2rem;margin-bottom:0.75rem">📊</div>
        <div style="font-size:13px;font-weight:700;color:#FFFFFF;margin-bottom:0.4rem;letter-spacing:-0.2px">
            Agent 1 · Transaction Analysis
        </div>
        <div style="font-size:11.5px;color:rgba(255,255,255,0.45);line-height:1.65;margin-bottom:0.9rem">
            Extracts suspicious indicators from raw transaction fields using 5 weighted flag rules.
            Computes a risk score (0–100) and derives tier: LOW · MEDIUM · HIGH · CRITICAL.
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;">
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">Threshold Proximity</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">Fan-out Detection</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">Velocity Flags</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="{CARD_CSS}">
        <div style="font-size:2rem;margin-bottom:0.75rem">🔗</div>
        <div style="font-size:13px;font-weight:700;color:#FFFFFF;margin-bottom:0.4rem;letter-spacing:-0.2px">
            Agent 2 · Compliance Retrieval
        </div>
        <div style="font-size:11.5px;color:rgba(255,255,255,0.45);line-height:1.65;margin-bottom:0.9rem">
            Hybrid dense (BGE-small) + BM25 retrieval fused via RRF. A PyTorch cross-encoder
            reranker surfaces the single most relevant regulatory clause from PMLA, FATF, and RBI docs.
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;">
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">Hybrid RAG</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">RRF Fusion</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">PyTorch Reranker</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="{CARD_CSS}">
        <div style="font-size:2rem;margin-bottom:0.75rem">📋</div>
        <div style="font-size:13px;font-weight:700;color:#FFFFFF;margin-bottom:0.4rem;letter-spacing:-0.2px">
            Agent 3 · Report Generation
        </div>
        <div style="font-size:11.5px;color:rgba(255,255,255,0.45);line-height:1.65;margin-bottom:0.9rem">
            Groq (Llama 3.3-70B) generates a structured investigation report with cited evidence,
            recommended action (STR filing obligation), and confidence level — in strict JSON.
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;">
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">Llama 3.3-70B</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">JSON Mode</span>
            <span style="font-size:10px;padding:2px 8px;border-radius:12px;background:rgba(30,144,255,0.1);color:#60AFFF;border:1px solid rgba(30,144,255,0.2)">Citation-backed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
st.markdown("<div style='max-width:920px;margin:0 auto;padding:0 1rem 3rem;'>", unsafe_allow_html=True)
st.markdown("""
<div style="
    display:grid; grid-template-columns: repeat(4,1fr); gap:1rem;
    padding: 0.5rem 0;
">
    <div style="text-align:center;padding:1.2rem;background:rgba(255,255,255,0.025);border:1px solid rgba(30,144,255,0.1);border-radius:10px;">
        <div style="font-size:1.8rem;font-weight:800;color:#1E90FF">&lt;30s</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:3px">End-to-end latency</div>
    </div>
    <div style="text-align:center;padding:1.2rem;background:rgba(255,255,255,0.025);border:1px solid rgba(30,144,255,0.1);border-radius:10px;">
        <div style="font-size:1.8rem;font-weight:800;color:#1E90FF">3</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:3px">Autonomous agents</div>
    </div>
    <div style="text-align:center;padding:1.2rem;background:rgba(255,255,255,0.025);border:1px solid rgba(30,144,255,0.1);border-radius:10px;">
        <div style="font-size:1.8rem;font-weight:800;color:#1E90FF">100%</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:3px">Tier accuracy (eval)</div>
    </div>
    <div style="text-align:center;padding:1.2rem;background:rgba(255,255,255,0.025);border:1px solid rgba(30,144,255,0.1);border-radius:10px;">
        <div style="font-size:1.8rem;font-weight:800;color:#1E90FF">5</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:3px">Regulatory corpora</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
