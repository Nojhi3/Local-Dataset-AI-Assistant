from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import db as db_service


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db_service, "SQLITE_PATH", str(test_db), raising=False)
    db_service.init_db()
    with TestClient(app) as test_client:
        yield test_client


def test_upload_csv_success(client: TestClient):
    sample_path = Path("data/sample/employees.csv")
    with sample_path.open("rb") as stream:
        response = client.post(
            "/api/upload",
            files={"file": ("employees.csv", stream, "text/csv")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Dataset uploaded and stored successfully."
    assert payload["file_type"] == "csv"
    assert payload["row_count"] > 0
    assert payload["dataset_id"]


def test_upload_invalid_file_type(client: TestClient):
    response = client.post(
        "/api/upload",
        files={"file": ("bad.txt", b"not,supported", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_chat_without_dataset(client: TestClient):
    response = client.post("/api/chat", json={"question": "Who is in HR?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_id"] == db_service.DEFAULT_DATASET_ID
