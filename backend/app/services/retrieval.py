import json
import re

from app.logging_config import get_logger
from app.services.db import fetch_rows

logger = get_logger(__name__)


def retrieve_relevant_rows(dataset_id: str, question: str, limit: int = 6) -> list[dict]:
    rows = fetch_rows(dataset_id)
    tokens = _question_tokens(question)
    scored: list[tuple[int, dict]] = []

    for row in rows:
        content = row["row_text"].lower()
        score = sum(1 for token in tokens if token in content)
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    top_rows = [row for _, row in scored[:limit]]
    if top_rows:
        logger.info(
            "Retrieved rows by token match dataset_id=%s requested_limit=%s matched=%s",
            dataset_id,
            limit,
            len(top_rows),
        )
        return top_rows
    logger.info(
        "No token match found; falling back to first rows dataset_id=%s fallback_count=%s",
        dataset_id,
        min(limit, len(rows)),
    )
    return rows[: min(limit, len(rows))]


def build_context(rows: list[dict]) -> str:
    lines: list[str] = []
    for row in rows:
        record = json.loads(row["row_json"])
        lines.append(f"Row {row['row_index']}: {record}")
    return "\n".join(lines)


def _question_tokens(question: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9]+", question.lower()) if len(token) > 2]
