import time

from fastapi import FastAPI
from fastapi import Request

from app.logging_config import configure_logging, get_logger
from app.routes import chat, health, ingest
from app.services.db import init_db

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Local Dataset AI Assistant API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_db()
    logger.info("Application started and database initialized.")


@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled error during request %s %s", request.method, request.url.path)
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Request %s %s -> %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
