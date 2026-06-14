import json
import sqlite3
from typing import List, Optional

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            case_id     TEXT PRIMARY KEY,
            report_json TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info(f"SQLite initialised at {settings.sqlite_db_path}")


def save_case(case_id: str, report: dict) -> None:
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO cases (case_id, report_json) VALUES (?, ?)",
        (case_id, json.dumps(report)),
    )
    conn.commit()
    conn.close()
    logger.info(f"Case {case_id} saved")


def get_case(case_id: str) -> Optional[dict]:
    conn = _connect()
    row = conn.execute(
        "SELECT report_json FROM cases WHERE case_id = ?", (case_id,)
    ).fetchone()
    conn.close()
    return json.loads(row["report_json"]) if row else None


def list_all_cases() -> List[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT case_id, report_json, created_at FROM cases ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [
        {"case_id": r["case_id"], "created_at": r["created_at"], **json.loads(r["report_json"])}
        for r in rows
    ]
