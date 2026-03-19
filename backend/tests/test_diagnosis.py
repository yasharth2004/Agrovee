"""
Tests for Diagnosis Endpoints
POST   /api/v1/diagnosis/diagnose
GET    /api/v1/diagnosis/diagnose/{id}
GET    /api/v1/diagnosis/history
DELETE /api/v1/diagnosis/diagnose/{id}
GET    /api/v1/diagnosis/recent
"""

import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestCreateDiagnosis:
    """Tests for POST /diagnosis/diagnose."""

    def test_create_diagnosis_success(self, auth_client: TestClient, sample_image):
        with open(sample_image, "rb") as f:
            resp = auth_client.post(
                "/api/v1/diagnosis/diagnose",
                files={"image": ("crop.jpg", f, "image/jpeg")},
                data={"soil_type": "loamy", "location": "Mumbai", "season": "summer"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["image_filename"] == "crop.jpg"
        assert data["soil_type"] == "loamy"
        assert data["status"] in ("completed", "failed", "pending", "processing")

    def test_create_diagnosis_no_image(self, auth_client: TestClient):
        resp = auth_client.post("/api/v1/diagnosis/diagnose")
        assert resp.status_code == 422

    def test_create_diagnosis_invalid_type(self, auth_client: TestClient):
        fake_file = io.BytesIO(b"not an image")
        resp = auth_client.post(
            "/api/v1/diagnosis/diagnose",
            files={"image": ("file.txt", fake_file, "text/plain")},
        )
        assert resp.status_code == 400
        assert "Invalid file type" in resp.json()["detail"]

    def test_create_diagnosis_unauthenticated(self, client: TestClient, sample_image):
        with open(sample_image, "rb") as f:
            resp = client.post(
                "/api/v1/diagnosis/diagnose",
                files={"image": ("crop.jpg", f, "image/jpeg")},
            )
        assert resp.status_code == 403

    def test_create_diagnosis_without_optional_fields(self, auth_client: TestClient, sample_image):
        with open(sample_image, "rb") as f:
            resp = auth_client.post(
                "/api/v1/diagnosis/diagnose",
                files={"image": ("crop.jpg", f, "image/jpeg")},
            )
        assert resp.status_code == 201


class TestGetDiagnosis:
    """Tests for GET /diagnosis/diagnose/{id}."""

    def test_get_diagnosis_success(self, auth_client: TestClient, sample_diagnosis):
        resp = auth_client.get(f"/api/v1/diagnosis/diagnose/{sample_diagnosis.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == sample_diagnosis.id
        assert data["predicted_disease"] == "Tomato___Early_Blight"
        assert data["confidence_score"] == 92.5
        assert data["crop_type"] == "Tomato"
        assert data["risk_assessment"] == "HIGH"

    def test_get_diagnosis_not_found(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/diagnosis/diagnose/99999")
        assert resp.status_code == 404

    def test_get_diagnosis_other_user(self, admin_client: TestClient, sample_diagnosis):
        """Cannot access another user's diagnosis — returns 404."""
        resp = admin_client.get(f"/api/v1/diagnosis/diagnose/{sample_diagnosis.id}")
        assert resp.status_code == 404


class TestDiagnosisHistory:
    """Tests for GET /diagnosis/history."""

    def test_history_empty(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/diagnosis/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["diagnoses"] == []
        assert data["total"] == 0

    def test_history_with_records(self, auth_client: TestClient, sample_diagnosis):
        resp = auth_client.get("/api/v1/diagnosis/history")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["diagnoses"]) == 1
        assert data["diagnoses"][0]["id"] == sample_diagnosis.id

    def test_history_pagination(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/diagnosis/history?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["per_page"] == 5


class TestDeleteDiagnosis:
    """Tests for DELETE /diagnosis/diagnose/{id}."""

    def test_delete_diagnosis_success(self, auth_client: TestClient, sample_diagnosis):
        resp = auth_client.delete(f"/api/v1/diagnosis/diagnose/{sample_diagnosis.id}")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Verify deleted
        resp2 = auth_client.get(f"/api/v1/diagnosis/diagnose/{sample_diagnosis.id}")
        assert resp2.status_code == 404

    def test_delete_diagnosis_not_found(self, auth_client: TestClient):
        resp = auth_client.delete("/api/v1/diagnosis/diagnose/99999")
        assert resp.status_code == 404


class TestRecentDiagnoses:
    """Tests for GET /diagnosis/recent."""

    def test_recent_empty(self, auth_client: TestClient):
        resp = auth_client.get("/api/v1/diagnosis/recent")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_recent_with_record(self, auth_client: TestClient, sample_diagnosis):
        resp = auth_client.get("/api/v1/diagnosis/recent")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_diagnosis.id
