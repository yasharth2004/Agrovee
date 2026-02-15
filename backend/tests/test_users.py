"""
Tests for User Profile Endpoints
GET  /api/v1/users/profile
PUT  /api/v1/users/profile
POST /api/v1/users/change-password
GET  /api/v1/users/stats
DELETE /api/v1/users/account
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import TEST_USER_PASSWORD, TEST_USER_EMAIL


class TestGetProfile:
    """Tests for GET /users/profile."""

    def test_get_profile_success(self, auth_client: TestClient, test_user):
        resp = auth_client.get("/api/v1/users/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "created_at" in data

    def test_get_profile_unauthenticated(self, client: TestClient):
        resp = client.get("/api/v1/users/profile")
        assert resp.status_code == 403


class TestUpdateProfile:
    """Tests for PUT /users/profile."""

    def test_update_full_name(self, auth_client: TestClient):
        resp = auth_client.put(
            "/api/v1/users/profile",
            json={"full_name": "Updated Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    def test_update_location(self, auth_client: TestClient):
        resp = auth_client.put(
            "/api/v1/users/profile",
            json={"location": "New Delhi"},
        )
        assert resp.status_code == 200
        assert resp.json()["location"] == "New Delhi"

    def test_update_farm_size(self, auth_client: TestClient):
        resp = auth_client.put(
            "/api/v1/users/profile",
            json={"farm_size": "25 hectares"},
        )
        assert resp.status_code == 200
        assert resp.json()["farm_size"] == "25 hectares"

    def test_update_multiple_fields(self, auth_client: TestClient):
        resp = auth_client.put(
            "/api/v1/users/profile",
            json={
                "full_name": "Multi Update",
                "phone": "+11111111111",
                "location": "Gujarat",
                "farm_size": "100 acres",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Multi Update"
        assert data["phone"] == "+11111111111"
        assert data["location"] == "Gujarat"
        assert data["farm_size"] == "100 acres"

    def test_update_empty_body(self, auth_client: TestClient):
        resp = auth_client.put(
            "/api/v1/users/profile",
            json={},
        )
        assert resp.status_code == 200


class TestChangePassword:
    """Tests for POST /users/change-password."""

    def test_change_password_success(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/users/change-password",
            json={
                "old_password": TEST_USER_PASSWORD,
                "new_password": "NewSecure123!",
                "confirm_password": "NewSecure123!",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_change_password_wrong_old(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/users/change-password",
            json={
                "old_password": "WrongOldPass!",
                "new_password": "NewSecure123!",
                "confirm_password": "NewSecure123!",
            },
        )
        assert resp.status_code == 400
        assert "Incorrect current password" in resp.json()["detail"]

    def test_change_password_mismatch(self, auth_client: TestClient):
        resp = auth_client.post(
            "/api/v1/users/change-password",
            json={
                "old_password": TEST_USER_PASSWORD,
                "new_password": "NewSecure123!",
                "confirm_password": "MismatchPass!",
            },
        )
        assert resp.status_code == 400
        assert "do not match" in resp.json()["detail"]


class TestUserStats:
    """Tests for GET /users/stats."""

    def test_stats_empty(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/users/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_diagnoses"] == 0
        assert data["healthy_count"] == 0
        assert data["diseased_count"] == 0
        assert data["average_confidence"] == 0.0

    def test_stats_with_diagnosis(self, auth_client: TestClient, sample_diagnosis):
        resp = auth_client.get("/api/v1/users/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_diagnoses"] == 1
        assert data["diseased_count"] == 1
        assert data["average_confidence"] > 0


class TestDeleteAccount:
    """Tests for DELETE /users/account."""

    def test_delete_account_soft(self, auth_client: TestClient, db: Session):
        resp = auth_client.delete("/api/v1/users/account")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        from app.models.user import User
        user = db.query(User).filter(User.email == TEST_USER_EMAIL).first()
        assert user.is_active is False
