"""
Tests for Authentication Endpoints
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


class TestRegister:
    """Tests for user registration endpoint."""

    def test_register_success(self, client: TestClient):
        payload = {
            "email": "new@agrovee.com",
            "password": "SecurePass1!",
            "confirm_password": "SecurePass1!",
            "full_name": "New Farmer",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@agrovee.com"
        assert data["full_name"] == "New Farmer"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_password_mismatch(self, client: TestClient):
        payload = {
            "email": "mismatch@test.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword!",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        assert "Passwords do not match" in resp.json()["detail"]

    def test_register_duplicate_email(self, client: TestClient, test_user):
        payload = {
            "email": TEST_USER_EMAIL,
            "password": "AnotherPass1!",
            "confirm_password": "AnotherPass1!",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        payload = {
            "email": "not-an-email",
            "password": "ValidPassword1!",
            "confirm_password": "ValidPassword1!",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422

    def test_register_short_password(self, client: TestClient):
        payload = {
            "email": "short@test.com",
            "password": "short",
            "confirm_password": "short",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 422

    def test_register_with_optional_fields(self, client: TestClient):
        payload = {
            "email": "full@agri.com",
            "password": "FullRegister1!",
            "confirm_password": "FullRegister1!",
            "full_name": "Full Farmer",
            "phone": "+919876543210",
            "location": "Maharashtra",
            "farm_size": "10 acres",
        }
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["phone"] == "+919876543210"
        assert data["location"] == "Maharashtra"
        assert data["farm_size"] == "10 acres"


class TestLogin:
    """Tests for login endpoint."""

    def test_login_success(self, client: TestClient, test_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_wrong_password(self, client: TestClient, test_user):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": TEST_USER_EMAIL, "password": "WrongPassword!"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.com", "password": "AnyPassword1!"},
        )
        assert resp.status_code == 401

    def test_login_inactive_user(self, client: TestClient, db: Session):
        from tests.conftest import _create_user
        _create_user(db, email="inactive@test.com", password="Password123!", is_active=False)
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@test.com", "password": "Password123!"},
        )
        assert resp.status_code == 403


class TestMe:
    """Tests for GET /auth/me — uses auth_client (dependency override)."""

    def test_me_authenticated(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert resp.json()["email"] == TEST_USER_EMAIL

    def test_me_no_token(self, client: TestClient):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 403

    def test_me_invalid_token(self, client: TestClient):
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken123"},
        )
        assert resp.status_code in (401, 403)


class TestLogout:
    """Tests for POST /auth/logout."""

    def test_logout_success(self, auth_client: TestClient):
        resp = auth_client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_logout_no_auth(self, client: TestClient):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code == 403


class TestRefreshToken:
    """Tests for POST /auth/refresh."""

    def test_refresh_success(self, auth_client: TestClient):
        resp = auth_client.post("/api/v1/auth/refresh")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
