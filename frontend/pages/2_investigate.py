import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st
from utils import BACKEND_URL, logit_to_confidence, confidence_bar_html, render_sidebar

st.set_page_config(
    page_title="Investigate | FinSentinel",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_sidebar()

DEMO_CASES = {
    "— Select a demo case —": None,
    "🔴 Structuring (HIGH)": {
        "account_id": "C1001", "amount_inr": 985000,
        "velocity_24h": 1, "account_age_days": 420, "is_cross_border": False,
        "_desc": "₹9.85L just below ₹10L reporting threshold — classic structuring signal",
    },
    "🔴 Fan-out smurfing (CRITICAL)": {
        "account_id": "C1002", "amount_inr": 4500000,
        "velocity_24h": 7, "account_age_days": 12, "is_cross_border": False,
        "_desc": "7 transactions in 24h from a 12-day-old account — fan-out pattern",
    },
    "🟠 Cross-border layering (HIGH)": {
        "account_id": "C1003", "amount_inr": 2200000,
        "velocity_24h": 3, "account_age_days": 8, "is_cross_border": True,
        "_desc": "Cross-border from a new account with large amount — layering",
    },
    "🟢 Legitimate transfer (LOW)": {
        "account_id": "C1004", "amount_inr": 1800000,
        "velocity_24h": 1, "account_age_days": 847, "is_cross_border": False,
        "_desc": "Established account, single domestic transaction — salary disbursement",
    },
    "🟡 Conflicting signals (MEDIUM)": {
        "account_id": "C1005", "amount_inr": 1800000,
        "velocity_24h": 1, "account_age_days": 847, "is_cross_border": True,
        "_desc": "Old account + cross-border: elevated but not conclusive",
    },
}

TIER_COLORS = {"CRITICAL": "#D93025", "HIGH": "#E87722", "MEDIUM": "#D4A017", "LOW": "#1A8C36"}
TIER_ICONS  = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

# ── Check backend ─────────────────────────────────────────────────────────────
docs_indexed   = 0
backend_online = False
try:
    h = requests.get(BACKEND_URL.replace("/api", "") + "/health", timeout=3)
    docs_indexed   = h.json().get("qdrant_chunk_count", 0)
    backend_online = True
except Exception:
    pass

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1.5rem 0 0.5rem;">
    <div style="font-size:10.5px;color:rgba(255,255,255,0.35);letter-spacing:1.5px;font-weight:600;margin-bottom:6px">
        INVESTIGATE
    </div>
    <h1 style="font-size:1.9rem;font-weight:800;color:#FFFFFF;margin:0;letter-spacing:-0.3px">
        Transaction Investigation
    </h1>
    <p style="color:rgba(255,255,255,0.45);font-size:13.5px;margin-top:6px">
        Run the 3-agent compliance pipeline on any transaction.
        Reports are citation-backed and audit-ready.
    </p>
</div>
""", unsafe_allow_html=True)

if not backend_online:
    st.error("❌ Backend offline — run: `uvicorn app.api.main:app --reload`")
elif docs_indexed == 0:
    st.warning(
        "⚠️ Knowledge base is empty — go to **📄 Knowledge Base** and index regulatory PDFs first. "
        "Agent 2 will return no policy citations without indexed documents."
    )
else:
    st.success(f"✅ Backend online — {docs_indexed:,} chunks in knowledge base", icon="✅")

st.divider()

# ── Demo case selector ────────────────────────────────────────────────────────
st.markdown("#### Quick Load")
demo_key = st.selectbox(
    "Load a pre-built scenario",
    options=list(DEMO_CASES.keys()),
    label_visibility="collapsed",
)
demo = DEMO_CASES[demo_key]
if demo and demo.get("_desc"):
    st.markdown(
        f"<p style='font-size:12px;color:rgba(255,255,255,0.38);margin-top:-6px'>{demo['_desc']}</p>",
        unsafe_allow_html=True,
    )

st.markdown("#### Transaction Details")

col1, col2 = st.columns(2, gap="large")
with col1:
    account_id = st.text_input(
        "Account ID",
        value=demo["account_id"] if demo else "",
        placeholder="e.g. C1001",
        key=f"aid_{demo_key}",
    )
    amount_inr = st.number_input(
        "Amount (INR ₹)",
        min_value=0.0,
        value=float(demo["amount_inr"]) if demo else 0.0,
        step=10000.0,
        format="%.0f",
        key=f"amt_{demo_key}",
    )
    velocity_24h = st.number_input(
        "Transactions in last 24h",
        min_value=0,
        value=int(demo["velocity_24h"]) if demo else 0,
        step=1,
        key=f"vel_{demo_key}",
    )

with col2:
    account_age_days = st.number_input(
        "Account age (days)",
        min_value=0,
        value=int(demo["account_age_days"]) if demo else 0,
        step=1,
        key=f"age_{demo_key}",
    )
    is_cross_border = st.checkbox(
        "Cross-border transaction",
        value=bool(demo["is_cross_border"]) if demo else False,
        key=f"xb_{demo_key}",
    )
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    can_run = backend_online and bool(account_id.strip()) and amount_inr > 0
    run_btn = st.button(
        "▶  Run Investigation",
        type="primary",
        disabled=not can_run,
        use_container_width=True,
    )

if not can_run:
    st.caption("Enter Account ID and Amount > 0 to enable investigation.")

st.divider()

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    payload = {
        "account_id":      account_id.strip(),
        "amount_inr":      amount_inr,
        "velocity_24h":    velocity_24h,
        "account_age_days": account_age_days,
        "is_cross_border": is_cross_border,
    }
    with st.status("Running compliance investigation pipeline …", expanded=True) as status:
        st.write("⏳  Agent 1 — Transaction Analysis …")
        try:
            t0   = time.time()
            resp = requests.post(f"{BACKEND_URL}/investigate", json=payload, timeout=120)
            if resp.status_code != 200:
                status.update(label="Investigation failed", state="error")
                st.error(f"Error: {resp.json().get('detail', 'Unknown')}")
                st.stop()
            case_id = resp.json()["case_id"]
            elapsed = time.time() - t0
            st.write("✅  Agent 1 — Transaction Analysis complete")
            st.write("✅  Agent 2 — Compliance Retrieval complete")
            st.write("✅  Agent 3 — Report Generation complete")
            rr = requests.get(f"{BACKEND_URL}/report/{case_id}", timeout=30)
            if rr.status_code != 200:
                status.update(label="Report fetch failed", state="error")
                st.error("Report generated but could not be retrieved.")
                st.stop()
            report = rr.json()
            st.session_state.last_report = report
            status.update(
                label=f"Complete in {elapsed:.1f}s  ·  Case ID: {case_id}",
                state="complete",
            )
        except requests.exceptions.ConnectionError:
            status.update(label="Connection error", state="error")
            st.error("Cannot connect to backend.")
            st.stop()
        except requests.exceptions.Timeout:
            status.update(label="Timeout", state="error")
            st.error("Investigation timed out (>120 s). Check backend logs.")
            st.stop()

# ── Report display ────────────────────────────────────────────────────────────
if "last_report" not in st.session_state:
    st.session_state.last_report = None

if st.session_state.last_report:
    report = st.session_state.last_report
    tier   = report.get("raw_risk_tier",  report.get("risk_tier",  "LOW"))
    score  = report.get("raw_risk_score", report.get("risk_score", 0))
    tcolor = TIER_COLORS.get(tier, "#888880")
    ticon  = TIER_ICONS.get(tier, "⚪")

    # Render report header as a clean, single full-width element
    st.markdown(
        f"<h3 style='margin:0 0 0.5rem 0;color:#FFFFFF'>Report — Case {report.get('case_id','')}</h3>",
        unsafe_allow_html=True,
    )
    
    # Risk banner
    st.markdown(f"""
    <div style="
        background: rgba(0,0,0,0.35);
        border: 1px solid {tcolor}44;
        border-left: 4px solid {tcolor};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        display:flex; align-items:center; gap: 1.5rem;
    ">
        <div>
            <div style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:600;letter-spacing:1.2px">RISK SCORE</div>
            <div style="font-size:2rem;font-weight:800;color:#FFFFFF;line-height:1">{score:.0f}<span style="font-size:1rem;color:rgba(255,255,255,0.3)">/100</span></div>
        </div>
        <div style="width:1px;height:48px;background:rgba(255,255,255,0.1)"></div>
        <div>
            <div style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:600;letter-spacing:1.2px">RISK TIER</div>
            <div style="font-size:2rem;font-weight:800;color:{tcolor};line-height:1">{ticon} {tier}</div>
        </div>
        <div style="width:1px;height:48px;background:rgba(255,255,255,0.1)"></div>
        <div>
            <div style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:600;letter-spacing:1.2px">CONFIDENCE</div>
            <div style="font-size:2rem;font-weight:800;color:#60AFFF;line-height:1">{report.get('confidence_level','—')}</div>
        </div>
        <div style="width:1px;height:48px;background:rgba(255,255,255,0.1)"></div>
        <div>
            <div style="font-size:10px;color:rgba(255,255,255,0.4);font-weight:600;letter-spacing:1.2px">INDICATORS</div>
            <div style="font-size:2rem;font-weight:800;color:#FFFFFF;line-height:1">{len(report.get('raw_indicators',[]))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recommended action block
    action = report.get("recommended_action", "")
    if action:
        bg = tcolor + "22"
        st.markdown(f"""
        <div style="
            background:{bg}; border:1px solid {tcolor}55;
            border-radius:8px; padding:0.85rem 1.1rem; margin:0.5rem 0;
        ">
            <span style="font-size:10px;font-weight:700;color:{tcolor};letter-spacing:1px">RECOMMENDED ACTION</span><br>
            <span style="font-size:13.5px;color:#FFFFFF;font-weight:500">{action}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        # Suspicious indicators
        st.markdown("##### Suspicious Indicators")
        indicators = report.get("raw_indicators", [])
        if indicators:
            pills = " ".join(
                f"<span style='display:inline-block;margin:2px;padding:4px 10px;"
                f"border-radius:20px;background:rgba(232,119,34,0.15);"
                f"border:1px solid rgba(232,119,34,0.35);color:#E87722;"
                f"font-size:12px;font-weight:500'>{i.replace('_',' ')}</span>"
                for i in indicators
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:rgba(255,255,255,0.35);font-size:13px'>No indicators triggered.</span>",
                        unsafe_allow_html=True)

        # Scoring rationale
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        st.markdown("##### Scoring Rationale")
        rationale = report.get("scoring_rationale", "—")
        parts = [p.strip() for p in rationale.split(";") if p.strip()]
        if len(parts) > 1:
            for p in parts:
                st.markdown(f"<p style='font-size:13px;color:rgba(255,255,255,0.6);margin:3px 0'>• {p}</p>",
                            unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='font-size:13px;color:rgba(255,255,255,0.6)'>{rationale}</p>",
                        unsafe_allow_html=True)

        # Transaction summary
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        st.markdown("##### Transaction Summary")
        st.markdown(f"<p style='font-size:13px;color:rgba(255,255,255,0.6)'>{report.get('transaction_summary','—')}</p>",
                    unsafe_allow_html=True)

    with col_r:
        # Suspicious patterns (LLM)
        st.markdown("##### Suspicious Patterns (AI Analysis)")
        patterns = [p for p in report.get("suspicious_patterns", [])
                    if isinstance(p, str) and len(p.strip()) > 3]
        if patterns:
            for p in patterns:
                st.markdown(f"<p style='font-size:13px;color:rgba(255,255,255,0.6);margin:3px 0'>• {p}</p>",
                            unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:rgba(255,255,255,0.35);font-size:13px'>No patterns identified.</span>",
                        unsafe_allow_html=True)

        # Policy citations (LLM)
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        st.markdown("##### Policy Citations")
        llm_cits = [c for c in report.get("policy_citations", [])
                    if isinstance(c, str) and len(c.strip()) > 5
                    and not c.strip().isdigit()
                    and not c.strip() in ("*", "2*", "")]
        if llm_cits:
            for c in llm_cits:
                st.markdown(
                    f"<div style='padding:6px 10px;margin:4px 0;"
                    f"background:rgba(30,144,255,0.07);"
                    f"border-left:2px solid #1E90FF;"
                    f"border-radius:4px;font-size:12.5px;color:rgba(255,255,255,0.75)'>{c}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<span style='color:rgba(255,255,255,0.35);font-size:13px'>"
                "No regulation references cited. Ensure documents are indexed and "
                "the investigation references specific regulatory clauses.</span>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Retrieved Policy Evidence (RAG) ────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:0.5rem'>
        <h5 style='color:#FFFFFF;margin-bottom:2px'>Retrieved Policy Evidence</h5>
        <p style='font-size:12px;color:rgba(255,255,255,0.35);margin:0'>
            These are the actual regulatory document chunks retrieved by Agent 2 (hybrid RAG pipeline).
            Confidence % is computed from the cross-encoder reranker score via sigmoid normalisation —
            a higher score means the chunk is more semantically relevant to the specific indicator query.
        </p>
    </div>
    """, unsafe_allow_html=True)

    raw_cits = report.get("raw_citations", [])
    if raw_cits:
        for i, cit in enumerate(raw_cits):
            raw_score  = cit.get("relevance_score", 0)
            conf       = logit_to_confidence(raw_score)
            doc_type   = cit.get("doc_type", "") or "REG"
            indicator  = cit.get("indicator", "").replace("_", " ")
            page_num   = cit.get("page", 0)
            source     = cit.get("source", "")

            with st.expander(
                f"[{doc_type}]  Indicator: {indicator}  ·  Page {page_num}  ·  "
                f"Confidence: {conf:.1f}%",
                expanded=(i == 0),
            ):
                # Confidence bar
                st.markdown(
                    confidence_bar_html(conf, label="Retrieval confidence"),
                    unsafe_allow_html=True,
                )
                if source:
                    st.markdown(
                        f"<p style='font-size:11px;color:rgba(255,255,255,0.3);margin:4px 0 8px'>"
                        f"Source: {os.path.basename(source)}</p>",
                        unsafe_allow_html=True,
                    )
                chunk_text = cit.get("chunk_text", "").strip()
                st.markdown(
                    f"<div style='font-size:13px;color:rgba(255,255,255,0.7);"
                    f"line-height:1.65;padding:8px;background:rgba(255,255,255,0.03);"
                    f"border-radius:6px'>{chunk_text}</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.info(
            "No policy evidence retrieved. Index regulatory PDFs in the Knowledge Base, then re-run."
        )

    st.divider()
    with st.expander("📋 Raw JSON Report"):
        st.json(report)
