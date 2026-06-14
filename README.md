# FinSentinel

**Agentic Financial Compliance Investigation System**  
Hybrid RAG · LangGraph · Gemini 1.5 Flash · PyTorch Reranker · FastAPI · Streamlit

---

## Overview

FinSentinel automates the research and documentation burden of AML compliance investigation. A compliance analyst submits a suspicious transaction; the system returns a structured, citation-backed investigation report in under 30 seconds — grounded in RBI, PMLA, FATF, and FIU-IND regulations.

```
Transaction Input
       │
       ▼
┌──────────────────┐
│   Agent 1        │  Extracts suspicious indicators, computes
│   Transaction    │  weighted risk score (0–100), derives tier
│   Analysis       │  LOW │ MEDIUM │ HIGH │ CRITICAL
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Agent 2        │  Dense (Qdrant BGE-small) + Sparse (BM25)
│   Compliance     │  → RRF fusion → PyTorch cross-encoder reranker
│   Retrieval      │  → top-3 cited regulatory chunks
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Agent 3        │  Gemini 1.5 Flash generates structured
│   Report         │  investigation report with JSON output —
│   Generation     │  cited, explainable, audit-ready
└──────────────────┘
```

---

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Hybrid RAG (dense + BM25)** | BM25 catches regulatory clause numbers (e.g. "PMLA §12") that dense embeddings smear into semantics |
| **RRF fusion (k=60)** | Parameter-free rank fusion; no training data required |
| **PyTorch cross-encoder reranker** | Full cross-attention on (query, chunk) pairs; reliably pushes most relevant clause to rank 1; <100ms on CPU |
| **LangGraph over vanilla LangChain** | Typed state graph with observable transitions; each node is independently retryable; execution trace visible in UI |
| **Gemini 1.5 Flash** | Free tier; large context window; reliable JSON output; avoids GPT-4 cost for iterative development |
| **Qdrant in-memory** | No cloud dependency; portable demo; no Docker required |
| **BGE-small-en-v1.5** | Top MTEB retrieval score at 33M params; fully local; no API call for embeddings |
| **Prompts externalised** | Separate `.txt` files per agent enable prompt iteration without Python file edits |

---

## Tech Stack

```
Backend         FastAPI + Uvicorn
Orchestration   LangGraph (StateGraph, typed nodes)
LLM             Gemini 1.5 Flash (google-generativeai)
Embeddings      BAAI/bge-small-en-v1.5 (SentenceTransformers)
Vector DB       Qdrant in-memory (qdrant-client)
Sparse Index    BM25Okapi (rank-bm25)
Reranker        cross-encoder/ms-marco-MiniLM-L-6-v2 (PyTorch)
Document Load   PyMuPDF (langchain-community)
Frontend        Streamlit
Persistence     SQLite
Evaluation      Custom tier accuracy + indicator recall metrics
Testing         pytest
```

---

## Project Structure

```
FinSentinel/
├── app/
│   ├── core/
│   │   ├── config.py              Pydantic Settings — all tuneable parameters
│   │   └── logger.py              Structured logging for all modules
│   ├── ingestion/
│   │   ├── loader.py              PyMuPDFLoader wrapper with metadata
│   │   ├── chunker.py             RecursiveCharacterTextSplitter (500/50)
│   │   ├── embedder.py            BGE-small local embeddings + embed_text()
│   │   └── pipeline.py            Orchestrates full ingest flow
│   ├── retrieval/
│   │   ├── qdrant_store.py        Qdrant in-memory client, upsert, dense search
│   │   ├── bm25_index.py          BM25Okapi build, pickle, load, search
│   │   ├── rrf_fusion.py          Pure Python RRF — Σ 1/(60+rank)
│   │   ├── reranker.py            PyTorch cross-encoder reranker
│   │   └── hybrid_retrieve.py     Public API — full retrieval pipeline
│   ├── agents/
│   │   ├── state.py               ComplianceInvestigationState TypedDict
│   │   ├── transaction_analysis.py Agent 1 — flag rules + risk scoring
│   │   ├── compliance_retrieval.py Agent 2 — per-indicator retrieval
│   │   ├── report_generation.py   Agent 3 — Gemini report + SQLite save
│   │   └── graph.py               LangGraph StateGraph compilation
│   ├── prompts/
│   │   ├── transaction_analysis.txt
│   │   ├── compliance_retrieval.txt
│   │   └── report_generation.txt
│   ├── api/
│   │   ├── main.py                FastAPI app, CORS, lifespan
│   │   ├── routes/
│   │   │   ├── ingest.py          POST /api/ingest
│   │   │   ├── investigate.py     POST /api/investigate
│   │   │   └── report.py          GET  /api/report/{case_id}
│   │   └── models/
│   │       ├── transaction.py     TransactionInput Pydantic model
│   │       └── report.py          ReportResponse Pydantic model
│   ├── store/
│   │   └── case_store.py          SQLite save/get/list
│   └── evaluation/
│       ├── eval_dataset.py        10 ground-truth evaluation cases
│       └── run_eval.py            Tier accuracy + indicator recall runner
├── frontend/
│   ├── app.py                     Streamlit home page
│   └── pages/
│       ├── 1_knowledge_base.py    PDF upload + indexing UI
│       └── 2_investigate.py       Investigation form + report display
├── scripts/
│   ├── demo_cases.py              4 pre-built investigation scenarios
│   └── seed_data.py               Synthetic transaction generator
├── tests/
│   ├── conftest.py                Shared pytest fixtures
│   ├── test_phase0.py             Config, logger, demo data
│   ├── test_phase1.py             RRF fusion, retrieval logic
│   ├── test_phase2.py             Agent flag logic, risk scoring
│   ├── test_phase3.py             API endpoints, case store
│   └── test_phase4.py             Evaluation dataset and metrics
├── notebooks/
│   ├── ragas_eval_analysis.ipynb  RAGAS metric visualisation
│   └── retrieval_debug.ipynb      Dense vs BM25 vs hybrid comparison
├── data/
│   ├── docs/                      Regulatory PDFs (user-supplied)
│   └── transactions/              Demo cases JSON
├── .env.example                   API key template
├── requirements.txt
├── pytest.ini
└── setup.md                       Step-by-step setup guide
```

---

## Quick Start

```bash
# Clone and enter
git clone https://github.com/your-username/FinSentinel.git && cd FinSentinel

# Install
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env → add GEMINI_API_KEY

# Demo data
python scripts/demo_cases.py

# Start backend (Terminal 1)
uvicorn app.api.main:app --reload --port 8000

# Start frontend (Terminal 2)
streamlit run frontend/app.py
```

Open [http://localhost:8501](http://localhost:8501). Upload a regulatory PDF, then run an investigation.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Backend health + Qdrant chunk count |
| `POST` | `/api/ingest` | Upload PDF, index to Qdrant + BM25 |
| `POST` | `/api/investigate` | Run 3-agent pipeline, return `case_id` |
| `GET` | `/api/report/{case_id}` | Retrieve investigation report JSON |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Investigation Demo Cases

| Scenario | Account | Amount | Velocity | Age | Cross-border | Expected Tier |
|----------|---------|--------|----------|-----|--------------|---------------|
| Structuring | C1001 | ₹9.85L | 1 | 420d | No | **HIGH** |
| Fan-out smurfing | C1002 | ₹45L | 7 | 12d | No | **CRITICAL** |
| Cross-border layering | C1003 | ₹22L | 3 | 8d | Yes | **HIGH** |
| Legitimate transfer | C1004 | ₹18L | 1 | 847d | No | **LOW** |
| Conflicting signals | C1005 | ₹18L | 1 | 847d | Yes | **MEDIUM** |

---

## Running Tests

```bash
pytest tests/ -v                    # All phases
pytest tests/test_phase2.py -v      # Agent logic only
pytest tests/ -v --tb=short         # Compact traceback
```

All tests are offline — no backend, API keys, or indexed documents required.

---

## Resume Block

**FinSentinel — Agentic Financial Compliance Investigation System** *(Python · LangGraph · RAG · PyTorch)*

- Designed and implemented a **3-agent LangGraph pipeline** for automated AML compliance investigation, producing citation-backed investigation reports grounded in RBI/PMLA/FATF regulatory corpora.
- Built a **hybrid RAG retrieval system** combining dense (BAAI/bge-small-en-v1.5) and sparse (BM25Okapi) retrieval with RRF fusion and a **PyTorch cross-encoder reranker** (ms-marco-MiniLM-L-6-v2), achieving <100ms reranking on CPU.
- Integrated **Gemini 1.5 Flash** for structured JSON report generation with full citation traceability; designed fallback logic ensuring report completeness even on LLM failure.
- Delivered a **FastAPI backend** (3 endpoints, SQLite persistence, Qdrant in-memory vector store) and a **Streamlit frontend** with live agent execution trace and expandable policy evidence citations.
- Implemented **custom evaluation metrics** (tier accuracy, indicator recall) on 10 ground-truth cases; validated 100% tier accuracy and indicator recall on the rule-based analysis layer.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Built as a focused 5-day MVP demonstrating production-grade RAG engineering for the RegTech domain.*
