import os
import sys
from pathlib import Path

import requests


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
SAMPLE_FILE = Path("data/sample/employees.csv")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    sys.exit(1)


def main() -> None:
    if not SAMPLE_FILE.exists():
        fail(f"Missing sample file: {SAMPLE_FILE}")

    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=10)
    except Exception as exc:
        fail(f"Cannot reach backend at {BACKEND_URL}: {exc}")

    if health.status_code != 200:
        fail(f"/health returned {health.status_code}")

    with SAMPLE_FILE.open("rb") as f:
        upload = requests.post(
            f"{BACKEND_URL}/api/upload",
            files={"file": (SAMPLE_FILE.name, f, "text/csv")},
            timeout=30,
        )

    if upload.status_code != 200:
        fail(f"/api/upload returned {upload.status_code}: {upload.text}")

    upload_payload = upload.json()
    dataset_id = upload_payload.get("dataset_id")
    if not dataset_id:
        fail("Upload response missing dataset_id")

    datasets = requests.get(f"{BACKEND_URL}/api/datasets", timeout=10)
    if datasets.status_code != 200:
        fail(f"/api/datasets returned {datasets.status_code}")
    if dataset_id not in {d["id"] for d in datasets.json().get("datasets", [])}:
        fail("Uploaded dataset_id not found in /api/datasets")

    chat = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={"question": "Which employee works in HR?", "dataset_id": dataset_id},
        timeout=60,
    )
    if chat.status_code != 200:
        fail(f"/api/chat returned {chat.status_code}: {chat.text}")

    answer = chat.json().get("answer", "").strip()
    if not answer:
        fail("Chat returned empty answer")

    print("[PASS] Smoke test complete")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Dataset ID: {dataset_id}")
    print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
