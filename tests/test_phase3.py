"""Phase 3 tests — API endpoints, Pydantic models, case store.

sentence_transformers is mocked so tests run without the large ML package.
"""
import sys
from unittest.mock import MagicMock

# ── Mock heavy ML deps before any app imports ─────────────────────────────────
_st_mock = MagicMock()
_st_mock.SentenceTransformer.return_value.encode.return_value = [[0.1] * 384]
_st_mock.CrossEncoder.return_value.predict.return_value = [0.9, 0.7, 0.5]
sys.modules.setdefault("sentence_transformers", _st_mock)

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.store.case_store import get_case, init_db, list_all_cases, save_case


# ── Case Store ────────────────────────────────────────────────────────────────

def test_init_db_succeeds():
    init_db()


def test_save_and_retrieve_case():
    init_db()
    save_case("TEST01", {"case_id": "TEST01", "risk_tier": "HIGH", "risk_score": 65.0})
    retrieved = get_case("TEST01")
    assert retrieved is not None
    assert retrieved["case_id"] == "TEST01"
    assert retrieved["risk_tier"] == "HIGH"


def test_get_nonexistent_case_returns_none():
    init_db()
    assert get_case("NONEXISTENT_XYZ") is None


def test_list_all_cases_returns_list():
    init_db()
    save_case("LIST01", {"case_id": "LIST01", "risk_tier": "LOW", "risk_score": 20.0})
    cases = list_all_cases()
    assert isinstance(cases, list)
    assert any(c["case_id"] == "LIST01" for c in cases)


def test_overwrite_existing_case():
    init_db()
    save_case("DUP01", {"case_id": "DUP01", "risk_tier": "LOW"})
    save_case("DUP01", {"case_id": "DUP01", "risk_tier": "CRITICAL"})
    assert get_case("DUP01")["risk_tier"] == "CRITICAL"


# ── Pydantic Models ───────────────────────────────────────────────────────────

def test_transaction_input_valid():
    from app.api.models.transaction import TransactionInput
    txn = TransactionInput(
        account_id="ACC001", amount_inr=500000.0,
        velocity_24h=3, account_age_days=180, is_cross_border=False,
    )
    assert txn.account_id == "ACC001"
    assert txn.amount_inr == 500000.0


def test_transaction_input_rejects_zero_amount():
    from pydantic import ValidationError
    from app.api.models.transaction import TransactionInput
    with pytest.raises(ValidationError):
        TransactionInput(account_id="A", amount_inr=0.0,
                         velocity_24h=1, account_age_days=100, is_cross_border=False)


def test_transaction_input_rejects_negative_amount():
    from pydantic import ValidationError
    from app.api.models.transaction import TransactionInput
    with pytest.raises(ValidationError):
        TransactionInput(account_id="A", amount_inr=-500.0,
                         velocity_24h=1, account_age_days=100, is_cross_border=False)


def test_transaction_model_serialises():
    from app.api.models.transaction import TransactionInput
    txn = TransactionInput(account_id="ACC002", amount_inr=750000.0,
                           velocity_24h=2, account_age_days=365, is_cross_border=True)
    d = txn.model_dump()
    assert d["account_id"] == "ACC002"
    assert d["is_cross_border"] is True


# ── FastAPI Endpoints ─────────────────────────────────────────────────────────

def test_health_endpoint():
    with TestClient(app) as c:
        response = c.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "qdrant_chunk_count" in data


def test_ingest_rejects_non_pdf():
    with TestClient(app) as c:
        response = c.post(
            "/api/ingest",
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
            data={"doc_type": "AML"},
        )
    assert response.status_code == 400


def test_report_not_found_returns_404():
    with TestClient(app) as c:  # lifespan runs → init_db called
        response = c.get("/api/report/XXXXXXXX")
    assert response.status_code == 404


def test_report_found_after_direct_save():
    init_db()
    save_case("APITEST01", {"case_id": "APITEST01", "risk_tier": "MEDIUM", "risk_score": 35.0})
    with TestClient(app) as c:
        response = c.get("/api/report/APITEST01")
    assert response.status_code == 200
    assert response.json()["risk_tier"] == "MEDIUM"


def test_openapi_docs_available():
    with TestClient(app) as c:
        response = c.get("/docs")
    assert response.status_code == 200


def test_investigate_endpoint_requires_all_fields():
    with TestClient(app) as c:
        response = c.post(
            "/api/investigate",
            json={"account_id": "TEST", "amount_inr": 500000, "velocity_24h": 1, "account_age_days": 100},
        )
    assert response.status_code == 422
