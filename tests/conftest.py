import os
import pytest


@pytest.fixture(autouse=True)
def use_test_database(tmp_path):
    from app.core import config
    original = config.settings.sqlite_db_path
    config.settings.sqlite_db_path = str(tmp_path / "test_finsentinel.db")
    yield
    config.settings.sqlite_db_path = original


@pytest.fixture(autouse=True)
def use_test_bm25(tmp_path):
    from app.core import config
    original = config.settings.bm25_pickle_path
    config.settings.bm25_pickle_path = str(tmp_path / "test_bm25.pkl")
    yield
    config.settings.bm25_pickle_path = original
