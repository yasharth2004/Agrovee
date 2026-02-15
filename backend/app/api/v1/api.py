"""
API v1 Router
Combines all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, diagnosis, chat

api_router = APIRouter()

# Authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# User routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Diagnosis routes
api_router.include_router(
    diagnosis.router,
    prefix="/diagnosis",
    tags=["Diagnosis"]
)

# Chat routes
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"]
)
