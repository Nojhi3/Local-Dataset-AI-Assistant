# Local Dataset AI Assistant

Starter scaffold for a local-only dataset chatbot demo.

## Stack
- Frontend: Streamlit
- Backend: FastAPI
- DB: SQLite
- Local LLM: Ollama
- Containerization: Docker Compose

## Quick Start (scaffold)
1. Set environment values in `.env` (already added to project root).
2. Run containers:
   - `docker compose up --build`
3. Open:
   - Frontend: `http://localhost:8501`
   - Backend docs: `http://localhost:8000/docs`

## Current Status
- Basic project structure and placeholder endpoints are ready.
- Ingestion and RAG logic are placeholders to be implemented next.
