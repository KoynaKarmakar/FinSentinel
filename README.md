# 🛡️ FinSentinel

> Agentic AML Compliance Investigation System powered by LangGraph, Hybrid RAG, Groq, and Cross-Encoder Reranking.

FinSentinel automates Anti-Money Laundering (AML) investigations by analyzing transaction behavior, retrieving relevant regulatory evidence, and generating structured, citation-backed compliance reports grounded in RBI, PMLA, FATF, and FIU-IND guidelines.

---

## ✨ Features

* 🚨 Transaction risk assessment and tier classification
* 🤖 Multi-agent investigation workflow using LangGraph
* 📚 Hybrid RAG (Dense + BM25 Retrieval)
* 🎯 Cross-Encoder reranking for regulatory evidence selection
* 📄 Citation-backed compliance reports
* ⚡ FastAPI backend with Streamlit dashboard
* 💾 SQLite-based case persistence
* 📊 Confidence-calibrated evidence scoring

---

## 🏗️ Architecture

```text
Transaction Input
       │
       ▼
┌──────────────────┐
│ Agent 1          │
│ Transaction      │
│ Analysis         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent 2          │
│ Compliance       │
│ Retrieval        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent 3          │
│ Report           │
│ Generation       │
└──────────────────┘
         │
         ▼
 Structured AML Investigation Report
```

### Workflow

1. **Transaction Analysis Agent**

   * Extracts suspicious indicators
   * Calculates weighted risk score (0–100)
   * Assigns LOW / MEDIUM / HIGH / CRITICAL tier

2. **Compliance Retrieval Agent**

   * Hybrid retrieval using Dense Search (BGE-small) + BM25
   * Reciprocal Rank Fusion (RRF)
   * Cross-Encoder reranking
   * Returns highest-confidence regulatory evidence

3. **Report Generation Agent**

   * Generates structured compliance investigation report
   * Provides explanations, citations, and recommended actions

---

## 🛠️ Tech Stack

| Component        | Technology             |
| ---------------- | ---------------------- |
| Orchestration    | LangGraph              |
| LLM              | Groq (Llama 3)         |
| Embeddings       | BAAI/bge-small-en-v1.5 |
| Vector Database  | Qdrant                 |
| Sparse Retrieval | BM25Okapi              |
| Reranker         | MiniLM Cross Encoder   |
| Backend          | FastAPI                |
| Frontend         | Streamlit              |
| Database         | SQLite                 |
| Testing          | Pytest                 |

---

## 🔍 Key Engineering Decisions

### Hybrid RAG

Combines:

* Dense Retrieval (BGE-small)
* Sparse Retrieval (BM25)

This improves retrieval of exact regulatory clauses while maintaining semantic understanding.

### Reciprocal Rank Fusion (RRF)

Merges dense and sparse retrieval results without requiring training data, improving recall across regulatory documents.

### Cross-Encoder Reranking

Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` to rerank retrieved chunks and ensure the most relevant compliance evidence is surfaced.

### Confidence Calibration

Applies custom sigmoid-based normalization to convert raw reranker scores into auditor-friendly confidence metrics.

### LangGraph Orchestration

Provides a typed, observable workflow where each investigation phase is isolated, retryable, and traceable.

---

## 📂 Project Structure

```text
FinSentinel/
├── app/
│   ├── agents/
│   ├── retrieval/
│   ├── ingestion/
│   ├── api/
│   ├── prompts/
│   └── store/
├── frontend/
├── scripts/
├── tests/
├── data/
└── requirements.txt
```

---

## 🚀 Quick Start

### Clone Repository

```bash
git clone https://github.com/KoynaKarmakar/FinSentinel.git
cd FinSentinel
```

### Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

```bash
cp .env.example .env
```

Add your API key:

```env
GROQ_API_KEY=your_api_key_here
```

### Run Backend

```bash
uvicorn app.api.main:app --reload --port 8000
```

### Run Frontend

```bash
streamlit run frontend/app.py
```

Open:

```text
http://localhost:8501
```

Upload regulatory documents, create investigation cases, and generate compliance reports.

---

## 📡 API Reference

| Method | Endpoint                | Description                             |
| ------ | ----------------------- | --------------------------------------- |
| GET    | `/health`               | Service health and retrieval statistics |
| POST   | `/api/ingest`           | Ingest compliance documents             |
| POST   | `/api/investigate`      | Execute AML investigation workflow      |
| GET    | `/api/report/{case_id}` | Retrieve generated investigation report |

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Run a specific module:

```bash
pytest tests/test_phase2.py -v
```

All tests run locally without requiring indexed documents or external services.

---

## 🎯 Sample Use Cases

* Transaction Structuring Detection
* Smurfing & Fan-Out Transfers
* Cross-Border Layering Analysis
* High-Risk Account Monitoring
* Regulatory Audit Preparation

---

## 🚀 Future Improvements

* Real-time transaction monitoring
* Multi-jurisdiction compliance support
* Analyst feedback loop
* Cloud deployment support
* Explainable risk scoring dashboard

---

## 👨‍💻 Author

**Koyna Karmakar**

AI/ML Engineer • LangGraph • RAG Systems • Financial AI

---

⭐ If you find this project useful, consider starring the repository.
