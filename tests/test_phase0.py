"""Phase 0 tests — config and logger."""
from app.core.config import settings
from app.core.logger import get_logger


def test_settings_chunk_size():
    assert settings.chunk_size == 500


def test_settings_chunk_overlap():
    assert settings.chunk_overlap == 50


def test_settings_top_k():
    assert settings.top_k == 10


def test_settings_risk_tier_ordering():
    assert settings.risk_tier_low < settings.risk_tier_medium
    assert settings.risk_tier_medium < settings.risk_tier_high


def test_settings_qdrant_collection():
    assert settings.qdrant_collection == "compliance_docs"


def test_logger_returns_logger():
    logger = get_logger("test.phase0")
    assert logger is not None
    assert logger.name == "test.phase0"


def test_logger_has_handler():
    logger = get_logger("test.handler")
    assert len(logger.handlers) > 0


def test_demo_cases_exist():
    from scripts.demo_cases import DEMO_CASES
    assert len(DEMO_CASES) == 4
    assert "Structuring" in DEMO_CASES
    assert "Fan-out smurfing" in DEMO_CASES
    assert "Cross-border layering" in DEMO_CASES
    assert "Legitimate transfer" in DEMO_CASES


def test_demo_cases_have_required_fields():
    from scripts.demo_cases import DEMO_CASES
    required = {"account_id", "amount_inr", "velocity_24h", "account_age_days", "is_cross_border"}
    for name, case in DEMO_CASES.items():
        assert required.issubset(case.keys()), f"Missing fields in case '{name}'"
