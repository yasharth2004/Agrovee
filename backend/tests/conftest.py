"""
Test Configuration and Fixtures
Provides test database, client, and authentication helpers
"""

import os
import sys
import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User
from app.models.diagnosis import Diagnosis, DiagnosisStatus
from app.models.chat import ChatSession, ChatMessage
from app.core.security import get_password_hash, create_access_token, get_current_user


# --------------- Database fixtures ---------------

TEST_DATABASE_URL = "sqlite://"  # in-memory

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Provide a clean database session per test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI test client with overridden DB dependency."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --------------- User / auth helpers ---------------

TEST_USER_EMAIL = "testuser@agrivision.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_ADMIN_EMAIL = "admin@agrivision.com"
TEST_ADMIN_PASSWORD = "Admin123!!"


def _create_user(
    db: Session,
    email: str = TEST_USER_EMAIL,
    password: str = TEST_USER_PASSWORD,
    full_name: str = "Test User",
    is_admin: bool = False,
    is_active: bool = True,
) -> User:
    """Insert a user directly into the test DB and return it."""
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        is_admin=is_admin,
        is_active=is_active,
        is_verified=True,
        location="Test City",
        phone="+1234567890",
        farm_size="5 acres",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _auth_header(user: User) -> Dict[str, str]:
    """Return Authorization header dict for a given user."""
    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_user(db: Session) -> User:
    """Create and return a regular test user."""
    return _create_user(db)


@pytest.fixture()
def admin_user(db: Session) -> User:
    """Create and return an admin user."""
    return _create_user(
        db,
        email=TEST_ADMIN_EMAIL,
        password=TEST_ADMIN_PASSWORD,
        full_name="Admin User",
        is_admin=True,
    )


def _make_auth_client(client_instance: TestClient, db: Session, user: User) -> TestClient:
    """Configure client with get_current_user override for a specific user."""

    def _override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = _override_get_current_user
    return client_instance


@pytest.fixture()
def auth_client(client: TestClient, db: Session, test_user: User) -> Generator[TestClient, None, None]:
    """Authenticated test client for regular user (overrides get_current_user)."""
    _make_auth_client(client, db, test_user)
    yield client


@pytest.fixture()
def admin_client(client: TestClient, db: Session, admin_user: User) -> Generator[TestClient, None, None]:
    """Authenticated test client for admin user."""
    _make_auth_client(client, db, admin_user)
    yield client


@pytest.fixture()
def auth_headers(test_user: User) -> Dict[str, str]:
    """Auth headers for the regular test user (used for login/register tests)."""
    return _auth_header(test_user)


@pytest.fixture()
def admin_headers(admin_user: User) -> Dict[str, str]:
    """Auth headers for the admin user."""
    return _auth_header(admin_user)


# --------------- Sample data fixtures ---------------

@pytest.fixture()
def sample_diagnosis(db: Session, test_user: User) -> Diagnosis:
    """Insert a completed sample diagnosis."""
    diagnosis = Diagnosis(
        user_id=test_user.id,
        image_path="/tmp/test_image.jpg",
        image_filename="test_image.jpg",
        image_size=1024,
        predicted_disease="Tomato___Early_Blight",
        confidence_score=92.5,
        crop_type="Tomato",
        model_version="1.0",
        all_predictions=[
            {"disease_name": "Tomato___Early_Blight", "probability": 92.5, "crop_type": "Tomato"},
            {"disease_name": "Tomato___Late_Blight", "probability": 4.2, "crop_type": "Tomato"},
        ],
        weather_data={"temperature": 28, "humidity": 75},
        soil_type="loamy",
        season="summer",
        fusion_confidence=89.0,
        risk_assessment="HIGH",
        recommendations={
            "immediate_actions": ["Remove infected leaves"],
            "treatments": [{"name": "Chlorothalonil", "dosage": "2g/L"}],
        },
        status=DiagnosisStatus.COMPLETED,
    )
    db.add(diagnosis)
    db.commit()
    db.refresh(diagnosis)
    return diagnosis


@pytest.fixture()
def sample_chat_session(db: Session, test_user: User) -> ChatSession:
    """Insert a chat session with messages."""
    session = ChatSession(
        user_id=test_user.id,
        title="Test Question",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Add a pair of messages
    for role, content in [
        ("user", "How to prevent early blight?"),
        ("assistant", "Early blight can be prevented by crop rotation and fungicides."),
    ]:
        msg = ChatMessage(session_id=session.id, role=role, content=content)
        db.add(msg)
    db.commit()
    db.refresh(session)
    return session


# --------------- Temporary image file fixture ---------------

@pytest.fixture()
def sample_image(tmp_path):
    """Create a minimal JPEG file for upload tests."""
    # Minimal valid JPEG bytes (2x2 white pixel)
    jpeg_bytes = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01"
        b"\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07"
        b"\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13"
        b"\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c"
        b"(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x02\x00\x02"
        b"\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01"
        b"\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04"
        b"\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03"
        b"\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00"
        b"\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B"
        b"\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()"
        b"*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87"
        b"\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4"
        b"\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba"
        b"\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7"
        b"\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2"
        b"\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00"
        b"\x00?\x00\xfb\xd2\x8a+\xff\xd9"
    )
    img_path = tmp_path / "test_crop.jpg"
    img_path.write_bytes(jpeg_bytes)
    return img_path
