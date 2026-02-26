"""
Tests for Health & Root Endpoints
GET /health
GET /
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests for GET /health."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint is reachable and returns healthy status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["service"] == "Agrovee API"

    def test_health_has_process_time_header(self, client: TestClient):
        """Response includes X-Process-Time header from middleware."""
        resp = client.get("/health")
        assert "x-process-time" in resp.headers


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_returns_welcome(self, client: TestClient):
        """Root endpoint returns welcome message."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "Agrovee" in data["message"]
        assert "version" in data
        assert data["docs"] == "/api/docs"
