import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from app.config import SQLITE_PATH
from app.logging_config import get_logger

logger = get_logger(__name__)


def _ensure_parent_dir() -> None:
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterable[sqlite3.Connection]:
    _ensure_parent_dir()
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT NOT NULL,
                row_index INTEGER NOT NULL,
                row_json TEXT NOT NULL,
                row_text TEXT NOT NULL,
                FOREIGN KEY(dataset_id) REFERENCES datasets(id)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_dataset ON records(dataset_id)"
        )
    logger.info("Database initialized at path=%s", SQLITE_PATH)


def insert_dataset(
    dataset_id: str, name: str, file_type: str, row_count: int, created_at: str
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO datasets (id, name, file_type, row_count, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (dataset_id, name, file_type, row_count, created_at),
        )
    logger.info("Inserted dataset metadata dataset_id=%s row_count=%s", dataset_id, row_count)


def insert_records(dataset_id: str, rows: list[dict[str, str]]) -> None:
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO records (dataset_id, row_index, row_json, row_text)
            VALUES (?, ?, ?, ?)
            """,
            [
                (dataset_id, idx, json.dumps(row, ensure_ascii=True), _row_to_text(row))
                for idx, row in enumerate(rows)
            ],
        )
    logger.info("Inserted records dataset_id=%s count=%s", dataset_id, len(rows))


def list_datasets() -> list[dict]:
    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT id, name, file_type, row_count, created_at
            FROM datasets
            ORDER BY created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in result]


def dataset_exists(dataset_id: str) -> bool:
    with get_connection() as conn:
        result = conn.execute(
            "SELECT 1 FROM datasets WHERE id = ? LIMIT 1", (dataset_id,)
        ).fetchone()
    return result is not None


def get_latest_dataset_id() -> str | None:
    with get_connection() as conn:
        result = conn.execute(
            "SELECT id FROM datasets ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
    return result["id"] if result else None


def fetch_rows(dataset_id: str) -> list[dict]:
    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT row_index, row_json, row_text
            FROM records
            WHERE dataset_id = ?
            ORDER BY row_index ASC
            """,
            (dataset_id,),
        ).fetchall()
    return [dict(row) for row in result]


def _row_to_text(row: dict[str, str]) -> str:
    parts = [f"{key}: {value}" for key, value in row.items()]
    return " | ".join(parts)
