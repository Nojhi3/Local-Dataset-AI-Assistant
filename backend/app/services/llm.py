import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.logging_config import get_logger

logger = get_logger(__name__)


def answer_from_context(question: str, context: str) -> str:
    logger.info(
        "Calling Ollama model=%s base_url=%s context_chars=%s",
        OLLAMA_MODEL,
        OLLAMA_BASE_URL,
        len(context),
    )
    prompt = (
        "You are a dataset QA assistant.\n"
        "Answer only from the provided CONTEXT.\n"
        "If the answer is not in context, reply exactly: "
        "'I don't know based on the uploaded dataset.'\n\n"
        f"QUESTION:\n{question}\n\n"
        f"CONTEXT:\n{context}\n"
    )
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    if response.status_code >= 400:
        detail = response.text
        try:
            payload = response.json()
            detail = payload.get("error", detail)
        except Exception:
            pass
        raise RuntimeError(
            f"Ollama request failed ({response.status_code}) at {OLLAMA_BASE_URL} "
            f"with model '{OLLAMA_MODEL}': {detail}"
        )
    data = response.json()
    logger.info("Ollama response received model=%s", OLLAMA_MODEL)
    return data.get("response", "").strip()
