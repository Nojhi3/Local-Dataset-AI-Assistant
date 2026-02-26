import io
import json
from typing import Any

import pandas as pd

from app.logging_config import get_logger

logger = get_logger(__name__)


def parse_tabular_file(filename: str, content: bytes) -> tuple[str, list[dict[str, str]]]:
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return "csv", _parse_csv(content)
    if lower_name.endswith(".json"):
        return "json", _parse_json(content)
    raise ValueError("Unsupported file type. Please upload a .csv or .json file.")


def _parse_csv(content: bytes) -> list[dict[str, str]]:
    frame = pd.read_csv(io.BytesIO(content), dtype=str).fillna("")
    rows = frame.to_dict(orient="records")
    logger.info("CSV parsed rows=%s columns=%s", len(rows), len(frame.columns))
    return [_normalize_row(row) for row in rows]


def _parse_json(content: bytes) -> list[dict[str, str]]:
    payload = json.loads(content.decode("utf-8"))
    if isinstance(payload, list):
        return [_normalize_row(item) for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if "records" in payload and isinstance(payload["records"], list):
            rows = [
                _normalize_row(item)
                for item in payload["records"]
                if isinstance(item, dict)
            ]
            logger.info("JSON parsed (records key) rows=%s", len(rows))
            return rows
        logger.info("JSON parsed single object.")
        return [_normalize_row(payload)]
    raise ValueError("JSON must be an object, list of objects, or {\"records\": [...]} format.")


def _normalize_row(row: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row.items():
        normalized[str(key)] = "" if value is None else str(value)
    return normalized
