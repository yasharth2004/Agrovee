"""
Schemas Package Initialization
"""

from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserProfile,
    UserUpdate,
    Token,
    PasswordChange
)
from app.schemas.diagnosis import (
    DiagnosisRequest,
    DiagnosisResponse,
    DiagnosisSummary,
    DiagnosisListResponse,
    DiagnosisStats
)
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionDetail,
    RAGResponse
)

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "UserProfile",
    "UserUpdate",
    "Token",
    "PasswordChange",
    # Diagnosis
    "DiagnosisRequest",
    "DiagnosisResponse",
    "DiagnosisSummary",
    "DiagnosisListResponse",
    "DiagnosisStats",
    # Chat
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatSessionResponse",
    "ChatSessionDetail",
    "RAGResponse"
]
