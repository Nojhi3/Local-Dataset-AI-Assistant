from fastapi import FastAPI

from app.routes import chat, health, ingest

app = FastAPI(title="Local Dataset AI Assistant API", version="0.1.0")

app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
