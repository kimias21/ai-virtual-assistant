"""
Tests for the FastAPI backend.

The Hugging Face call is mocked (`app.llm_client.generate_reply`) so the
suite runs offline/deterministically in CI without needing a real HF token
or network access.
"""
from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model" in body


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "service" in resp.json()


@patch("app.main.generate_reply", return_value="Hello there!")
def test_chat_happy_path(mock_generate):
    resp = client.post("/api/v1/chat", json={"message": "Hi", "history": []})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "Hello there!"
    assert "model" in body
    mock_generate.assert_called_once()


@patch("app.main.generate_reply", return_value="Second reply")
def test_chat_with_history(mock_generate):
    history = [
        {"role": "user", "content": "What is AI?"},
        {"role": "assistant", "content": "Artificial Intelligence."},
    ]
    resp = client.post("/api/v1/chat", json={"message": "Give an example", "history": history})
    assert resp.status_code == 200
    assert resp.json()["reply"] == "Second reply"


def test_chat_rejects_empty_message():
    resp = client.post("/api/v1/chat", json={"message": "", "history": []})
    assert resp.status_code == 422


@patch("app.main.generate_reply", side_effect=Exception("boom"))
def test_chat_upstream_failure_returns_502(mock_generate):
    from app.llm_client import LLMClientError

    mock_generate.side_effect = LLMClientError("HF API down")
    resp = client.post("/api/v1/chat", json={"message": "Hi", "history": []})
    assert resp.status_code == 502
