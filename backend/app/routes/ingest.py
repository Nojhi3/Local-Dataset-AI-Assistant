from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.logging_config import get_logger
from app.services.db import (
    init_db,
    insert_dataset,
    insert_records,
    list_datasets,
)
from app.services.parsing import parse_tabular_file

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict:
    init_db()
    if not file.filename:
        logger.warning("Upload rejected: missing filename.")
        raise HTTPException(status_code=400, detail="Filename is required.")

    content = await file.read()
    if not content:
        logger.warning("Upload rejected: empty file (%s).", file.filename)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        file_type, rows = parse_tabular_file(file.filename, content)
        logger.info(
            "Parsed upload file=%s file_type=%s row_count=%s",
            file.filename,
            file_type,
            len(rows),
        )
    except ValueError as exc:
        logger.warning("Upload parse validation failed for file=%s: %s", file.filename, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected parse failure for file=%s", file.filename)
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}") from exc

    if not rows:
        logger.warning("Upload rejected: no rows found in file=%s", file.filename)
        raise HTTPException(status_code=400, detail="No records found in uploaded file.")

    dataset_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    insert_dataset(
        dataset_id=dataset_id,
        name=file.filename,
        file_type=file_type,
        row_count=len(rows),
        created_at=created_at,
    )
    insert_records(dataset_id=dataset_id, rows=rows)
    logger.info("Dataset stored dataset_id=%s name=%s rows=%s", dataset_id, file.filename, len(rows))

    return {
        "message": "Dataset uploaded and stored successfully.",
        "dataset_id": dataset_id,
        "filename": file.filename,
        "file_type": file_type,
        "row_count": len(rows),
        "created_at": created_at,
    }


@router.get("/datasets")
def get_datasets() -> dict:
    init_db()
    datasets = list_datasets()
    logger.info("Returning dataset list count=%s", len(datasets))
    return {"datasets": datasets}
