# Local Dataset AI Assistant

Local-first AI chatbot demo for Q&A on uploaded CSV/JSON datasets.

## What Is Implemented
- Streamlit frontend for upload + chat.
- FastAPI backend with:
  - `POST /api/upload`
  - `GET /api/datasets`
  - `POST /api/chat`
  - `GET /health`
- SQLite storage for dataset metadata and records.
- Ollama integration for local model inference.
- Strict grounding behavior:
  - If no relevant retrieved context is found, response is:
    - `I don't know based on the uploaded dataset.`
- Smoke test and basic pytest coverage.
- Centralized backend logging (request logs + error logs).

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- Database: SQLite
- Local LLM: Ollama (`llama3.2:3b` recommended)
- Tests: `pytest` + smoke test script
- Containerization: Docker Compose

## Local Run (Without Docker)
1. Verify Ollama is running and model exists:
   - `ollama list`
   - if needed: `ollama pull llama3.2:3b`
2. Use local `.env` values:
   - `OLLAMA_BASE_URL=http://127.0.0.1:11434`
   - `OLLAMA_MODEL=llama3.2:3b`
   - `SQLITE_PATH=backend/data/app.db`
3. Start backend:
   - `cd backend`
   - `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
4. Start frontend (new terminal):
   - `cd frontend`
   - `streamlit run app.py --server.port 8501`
5. Open:
   - Frontend: `http://localhost:8501`
   - Backend docs: `http://localhost:8000/docs`

## Test Commands
- Smoke test:
  - `python smoke_test.py`
- Pytest:
  - `python -m pytest -q`

## Docker Run
1. Use Docker-oriented settings (backend service in compose already uses):
   - `OLLAMA_BASE_URL=http://ollama:11434`
   - `OLLAMA_MODEL=llama3.2:3b`
   - `SQLITE_PATH=/app/data/app.db`
2. Start stack:
   - `docker compose up --build -d`
3. Pull model in Ollama container (first run):
   - `docker exec -it lda-ollama ollama pull llama3.2:3b`
4. Validate:
   - Frontend: `http://localhost:8501`
   - Backend: `http://localhost:8000/health`
5. Stop:
   - `docker compose down`

## Current Remaining Work
- Final Docker end-to-end validation and screenshot/proof for submission.
- README/demo polish for final handoff.
- Optional enhancement: semantic retrieval (vector DB) for broader question matching.
