from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.logging_config import get_logger
from app.services.db import dataset_exists, get_latest_dataset_id, init_db
from app.services.llm import answer_from_context
from app.services.retrieval import build_context, retrieve_relevant_rows

router = APIRouter()
logger = get_logger(__name__)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2)
    dataset_id: str | None = None


@router.post("/chat")
def chat(request: ChatRequest) -> dict:
    init_db()
    dataset_id = request.dataset_id or get_latest_dataset_id()
    if not dataset_id:
        logger.warning("Chat rejected: no dataset available.")
        raise HTTPException(status_code=400, detail="No dataset found. Upload a dataset first.")
    if not dataset_exists(dataset_id):
        logger.warning("Chat rejected: dataset not found dataset_id=%s", dataset_id)
        raise HTTPException(status_code=404, detail="Dataset not found.")

    rows = retrieve_relevant_rows(dataset_id, request.question, limit=6)
    if not rows:
        logger.info("Chat has no relevant rows dataset_id=%s", dataset_id)
        return {
            "answer": "I don't know based on the uploaded dataset.",
            "dataset_id": dataset_id,
            "sources": [],
        }

    context = build_context(rows)
    try:
        answer = answer_from_context(request.question, context)
        logger.info(
            "Chat answered dataset_id=%s source_rows=%s",
            dataset_id,
            [row["row_index"] for row in rows],
        )
    except Exception as exc:
        logger.exception("Chat model call failed dataset_id=%s", dataset_id)
        answer = (
            "Model call failed. "
            f"{exc}"
        )

    return {
        "answer": answer,
        "dataset_id": dataset_id,
        "sources": [row["row_index"] for row in rows],
    }

