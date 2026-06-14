import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st
from utils import BACKEND_URL, render_sidebar

st.set_page_config(
    page_title="Knowledge Base | FinSentinel",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_sidebar()

# ── Backend health ────────────────────────────────────────────────────────────
chunk_count = 0
backend_online = False
try:
    health = requests.get(BACKEND_URL.replace("/api", "") + "/health", timeout=3)
    chunk_count = health.json().get("qdrant_chunk_count", 0)
    backend_online = True
except Exception:
    pass

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 1.5rem 0 0.5rem;">
    <div style="font-size:10.5px;color:rgba(255,255,255,0.35);letter-spacing:1.5px;font-weight:600;margin-bottom:6px">
        KNOWLEDGE BASE
    </div>
    <h1 style="font-size:1.9rem;font-weight:800;color:#FFFFFF;margin:0;letter-spacing:-0.3px">
        Regulatory Document Index
    </h1>
    <p style="color:rgba(255,255,255,0.45);font-size:13.5px;margin-top:6px">
        Upload compliance PDFs to populate the RAG knowledge base.
        All investigation reports cite chunks from these documents.
    </p>
</div>
""", unsafe_allow_html=True)

# Status banner
if not backend_online:
    st.error("❌ Backend offline — start with: `uvicorn app.api.main:app --reload`")
elif chunk_count > 0:
    st.success(f"✅ Backend connected — **{chunk_count:,}** chunks indexed across all documents")
else:
    st.warning("⚠️ Backend connected — knowledge base is empty. Upload at least one PDF below.")

st.divider()

# ── Upload section ────────────────────────────────────────────────────────────
st.markdown("#### Upload Document")

col_file, col_gap, col_type = st.columns([3, 0.15, 1])
with col_file:
    uploaded_file = st.file_uploader(
        "Select a PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Drag & drop or browse. Supported: RBI KYC, PMLA, FATF, FIU-IND STR, RBI Fraud Circular",
    )
with col_type:
    doc_type = st.selectbox(
        "Document type",
        options=["AML", "KYC", "STR", "RBI_Circular", "FATF"],
        help="Used for metadata-filtered retrieval inside Agent 2",
    )

col_btn, col_hint = st.columns([1.2, 4])
with col_btn:
    index_clicked = st.button(
        "Index Document",
        type="primary",
        disabled=(uploaded_file is None or not backend_online),
        use_container_width=True,
    )
with col_hint:
    if uploaded_file is None:
        st.markdown(
            "<span style='font-size:12px;color:rgba(255,255,255,0.3);line-height:3'>Select a PDF first</span>",
            unsafe_allow_html=True,
        )

if "indexed_docs" not in st.session_state:
    st.session_state.indexed_docs = []

if index_clicked and uploaded_file is not None:
    with st.spinner(f"Indexing {uploaded_file.name} …"):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/ingest",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                data={"doc_type": doc_type},
                timeout=180,
            )
            if resp.status_code == 200:
                data = resp.json()
                st.success(
                    f"✅ **{data['doc_name']}** indexed — "
                    f"**{data['chunk_count']}** chunks added  "
                    f"(knowledge base total: **{data['collection_total']}** chunks)"
                )
                st.session_state.indexed_docs.append({
                    "Document":     data["doc_name"],
                    "Type":         doc_type,
                    "Chunks Added": data["chunk_count"],
                    "KB Total":     data["collection_total"],
                })
            else:
                st.error(f"Indexing failed: {resp.json().get('detail', 'Unknown error')}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Check that the server is running.")
        except requests.exceptions.Timeout:
            st.error("Request timed out (>3 min). Try a smaller PDF first.")

st.divider()

# ── Indexed docs table ────────────────────────────────────────────────────────
st.markdown("#### Indexed Documents (this session)")

if st.session_state.indexed_docs:
    st.dataframe(
        st.session_state.indexed_docs,
        use_container_width=True,
        hide_index=True,
    )
    if st.button("Clear session log", type="secondary"):
        st.session_state.indexed_docs = []
        st.rerun()
else:
    st.markdown("""
    <div style="
        padding:2rem; text-align:center;
        background:rgba(255,255,255,0.025);
        border:1px dashed rgba(30,144,255,0.2);
        border-radius:12px; color:rgba(255,255,255,0.35);
        font-size:13px; line-height:1.8;
    ">
        No documents indexed yet.<br>
        <b style="color:rgba(255,255,255,0.55)">Recommended PDFs:</b><br>
        RBI KYC Master Direction 2016 &nbsp;·&nbsp;
        PMLA 2002 &nbsp;·&nbsp;
        FATF 40 Recommendations 2023 &nbsp;·&nbsp;
        FIU-IND STR Guidelines &nbsp;·&nbsp;
        RBI Master Circular on Fraud
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("""
<p style="font-size:11.5px;color:rgba(255,255,255,0.25);">
ℹ️  Qdrant runs in-memory — documents must be re-indexed if the backend server restarts.
BM25 index is pickled to <code>data/bm25.pkl</code> and reloaded automatically on startup.
</p>
""", unsafe_allow_html=True)
