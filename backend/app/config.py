import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_env(name: str, default: str) -> str:
    return os.getenv(name, default)


SQLITE_PATH = get_env("SQLITE_PATH", str(PROJECT_ROOT / "backend" / "data" / "app.db"))
OLLAMA_BASE_URL = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = get_env("OLLAMA_MODEL", "mistral")
RETRIEVAL_MIN_SCORE = int(get_env("RETRIEVAL_MIN_SCORE", "1"))
