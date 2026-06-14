# FinSentinel — Setup Guide

Follow every step in order. If you follow this guide blindly from a fresh clone, the project will run.

---

## Prerequisites

| Tool | Minimum Version | Check |
|------|----------------|-------|
| Python | 3.10 | `python --version` |
| pip | 23.0 | `pip --version` |
| Git | any | `git --version` |

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/FinSentinel.git
cd FinSentinel
```

---

## Step 2 — Create and activate a virtual environment

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

---

## Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> This installs all backend and frontend dependencies.  
> First-time install takes 3–8 minutes (downloads ML models ~500MB).

---

## Step 4 — Configure API keys

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace the placeholder:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

**Get a free Gemini API key:**  
Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → Sign in → Create API key → Copy it into `.env`.

> ⚠️ Never commit your `.env` file. It is already in `.gitignore`.

---

## Step 5 — Generate demo data

```bash
python scripts/demo_cases.py
```

This writes 4 pre-built investigation scenarios to `data/transactions/demo_cases.json`.

---

## Step 6 — Start the backend server

Open **Terminal 1** and run:

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

Wait until you see:
```
INFO | app.api.main | FinSentinel API ready
INFO:     Application startup complete.
```

Verify it is running:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"FinSentinel","qdrant_chunk_count":0}
```

Or open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for the Swagger UI.

---

## Step 7 — Download regulatory PDFs (knowledge base)

Download all five documents and save them anywhere on your computer:

| Document | Source |
|----------|--------|
| RBI KYC Master Direction 2016 | [rbi.org.in](https://rbi.org.in) — search "KYC Master Direction" |
| Prevention of Money Laundering Act 2002 | [indiacode.nic.in](https://indiacode.nic.in) — search "PMLA 2002" |
| FATF 40 Recommendations 2023 | [fatf-gafi.org/en/topics/fatf-recommendations.html](https://www.fatf-gafi.org/en/topics/fatf-recommendations.html) |
| FIU-IND STR Filing Guidelines | [fiuindia.gov.in](https://fiuindia.gov.in) — Reporting → STR |
| RBI Master Circular on Fraud | [rbi.org.in](https://rbi.org.in) — search "Master Circular Fraud" |

You will upload these via the UI in Step 9.

---

## Step 8 — Start the frontend

Open **Terminal 2** (keep Terminal 1 running) and run:

```bash
streamlit run frontend/app.py
```

Wait until you see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Step 9 — Index the regulatory PDFs

1. In the Streamlit UI, click **📄 Knowledge Base** in the left sidebar.
2. For each PDF you downloaded in Step 7:
   - Click **Browse files** and select the PDF.
   - Choose the correct **Document Type** from the dropdown (AML, KYC, FATF, etc.).
   - Click **Index Document**.
   - Wait for the success message showing chunk count.
3. Repeat for all 5 PDFs.

> After indexing, the Knowledge Base page shows a table of all indexed documents.

---

## Step 10 — Run your first investigation

1. Click **🔎 Investigate** in the left sidebar.
2. Under **Load Demo Case**, select **Structuring (HIGH)** from the dropdown.
3. Click **▶ Run Investigation**.
4. Watch the agent trace complete (takes 10–25 seconds).
5. Review the investigation report: risk score, indicators, cited policy evidence, and recommended action.

---

## Step 11 — Run tests

With the virtual environment active, run all tests from the project root:

```bash
pytest tests/ -v
```

Run a specific phase:
```bash
pytest tests/test_phase0.py -v   # Config and logger
pytest tests/test_phase1.py -v   # RRF fusion and retrieval logic
pytest tests/test_phase2.py -v   # Agent flag logic and risk scoring
pytest tests/test_phase3.py -v   # API endpoints and case store
pytest tests/test_phase4.py -v   # Evaluation dataset and metrics
```

Expected output: all tests pass. Tests do not require a live backend or API keys.

---

## Step 12 — Run the evaluation (optional)

With documents indexed and the backend running:

```bash
python -m app.evaluation.run_eval
```

This evaluates risk tier accuracy and indicator recall against 10 ground-truth cases.

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` and ensure your venv is active |
| `Connection refused` on port 8000 | Start the backend in Terminal 1: `uvicorn app.api.main:app --reload` |
| `GEMINI_API_KEY` error | Ensure `.env` exists with a valid key (not the placeholder) |
| Slow first investigation | Models (BGE-small + cross-encoder) load once on first use (~30s overhead) |
| Qdrant empty after restart | Re-upload PDFs in Knowledge Base — Qdrant is in-memory and does not persist across restarts |
| Port 8501 in use | Run `streamlit run frontend/app.py --server.port 8502` |
| Port 8000 in use | Run `uvicorn app.api.main:app --reload --port 8001` and update Backend URL in sidebar |

---

## Project Structure Reference

```
FinSentinel/
├── app/
│   ├── core/           Config + logging (Phase 0)
│   ├── ingestion/      PDF load → chunk → embed → upsert (Phase 1)
│   ├── retrieval/      Qdrant + BM25 + RRF + reranker (Phase 1)
│   ├── agents/         3 LangGraph nodes (Phase 2)
│   ├── prompts/        LLM prompt templates (Phase 2)
│   ├── api/            FastAPI routes + models (Phase 3)
│   ├── store/          SQLite case persistence (Phase 3)
│   └── evaluation/     RAGAS eval dataset + runner (Phase 4)
├── frontend/           Streamlit UI — 2 pages (Phase 3)
├── scripts/            Demo data generators (Phase 0)
├── tests/              One test file per phase
├── data/               PDFs + generated artifacts
├── notebooks/          Exploratory analysis
├── .env.example        API key template
├── requirements.txt    All dependencies
└── setup.md            This file
```
