import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


def resolve_sqlite_path(raw_path: str) -> str:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return str(candidate)
    return str((PROJECT_ROOT / candidate).resolve())


SQLITE_PATH = resolve_sqlite_path(
    get_env("SQLITE_PATH", str(PROJECT_ROOT / "backend" / "data" / "app.db"))
)
OLLAMA_BASE_URL = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "mistral")
RETRIEVAL_MIN_SCORE = int(get_env("RETRIEVAL_MIN_SCORE", "1"))
