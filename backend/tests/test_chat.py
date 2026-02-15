"""
Tests for Chat Endpoints
POST   /api/v1/chat/message
GET    /api/v1/chat/sessions
GET    /api/v1/chat/sessions/{id}
DELETE /api/v1/chat/sessions/{id}
PUT    /api/v1/chat/sessions/{id}/title
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestSendMessage:
    """Tests for POST /chat/message."""

    def test_send_message_new_session(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/chat/message",
            json={"content": "How do I prevent tomato blight?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "assistant"
        assert len(data["content"]) > 0
        assert "session_id" in data

    def test_send_message_existing_session(self, auth_client: TestClient, sample_chat_session):
        resp = auth_client.post(
            "/api/v1/chat/message",
            json={
                "content": "Tell me more about fungicides",
                "session_id": sample_chat_session.id,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["session_id"] == sample_chat_session.id

    def test_send_message_invalid_session(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/chat/message",
            json={"content": "Hello?", "session_id": 99999},
        )
        assert resp.status_code == 404

    def test_send_message_empty_content(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/chat/message",
            json={"content": ""},
        )
        assert resp.status_code == 422

    def test_send_message_with_context(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/chat/message",
            json={
                "content": "What fertilizer for rice?",
                "context": {"crop": "rice", "region": "Punjab"},
            },
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "assistant"

    def test_send_message_unauthenticated(self, client: TestClient):
        resp = client.post("/api/v1/chat/message", json={"content": "Hello"})
        assert resp.status_code == 403


class TestGetSessions:
    """Tests for GET /chat/sessions."""

    def test_sessions_empty(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/chat/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["sessions"] == []
        assert data["total"] == 0

    def test_sessions_with_record(self, auth_client: TestClient, sample_chat_session):
        resp = auth_client.get("/api/v1/chat/sessions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["sessions"][0]["id"] == sample_chat_session.id

    def test_sessions_pagination(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/chat/sessions?page=2&per_page=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 2
        assert data["per_page"] == 5


class TestGetSession:
    """Tests for GET /chat/sessions/{id}."""

    def test_get_session_with_messages(self, auth_client: TestClient, sample_chat_session):
        resp = auth_client.get(f"/api/v1/chat/sessions/{sample_chat_session.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == sample_chat_session.id
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    def test_get_session_not_found(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/chat/sessions/99999")
        assert resp.status_code == 404

    def test_get_session_other_user(self, admin_client: TestClient, sample_chat_session):
        resp = admin_client.get(f"/api/v1/chat/sessions/{sample_chat_session.id}")
        assert resp.status_code == 404


class TestDeleteSession:
    """Tests for DELETE /chat/sessions/{id}."""

    def test_delete_session_success(self, auth_client: TestClient, sample_chat_session):
        resp = auth_client.delete(f"/api/v1/chat/sessions/{sample_chat_session.id}")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        resp2 = auth_client.get(f"/api/v1/chat/sessions/{sample_chat_session.id}")
        assert resp2.status_code == 404

    def test_delete_session_not_found(self, auth_client: TestClient):
        resp = auth_client.delete("/api/v1/chat/sessions/99999")
        assert resp.status_code == 404


class TestUpdateSessionTitle:
    """Tests for PUT /chat/sessions/{id}/title."""

    def test_update_title_success(self, auth_client: TestClient, sample_chat_session):
        resp = auth_client.put(
            f"/api/v1/chat/sessions/{sample_chat_session.id}/title",
            params={"title": "Renamed Session"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        resp2 = auth_client.get(f"/api/v1/chat/sessions/{sample_chat_session.id}")
        assert resp2.json()["title"] == "Renamed Session"

    def test_update_title_not_found(self, auth_client: TestClient):
        resp = auth_client.put(
            "/api/v1/chat/sessions/99999/title",
            params={"title": "Nope"},
        )
        assert resp.status_code == 404
