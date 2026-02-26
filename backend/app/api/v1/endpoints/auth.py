"""
Authentication Endpoints
User registration, login, token refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse, PasswordResetRequest, PasswordResetConfirm
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from app.core.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory reset token store (production: use Redis/DB)
_reset_tokens: dict[str, tuple[str, datetime]] = {}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional user's full name
    """
    # Validate passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        location=user_data.location,
        farm_size=user_data.farm_size,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    Returns JWT access and refresh tokens
    """
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    Requires valid JWT token
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    Note: JWT tokens are stateless, so client should discard the token
    """
    return {
        "success": True,
        "message": "Successfully logged out"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    Returns new access and refresh tokens
    """
    # Create new tokens
    access_token = create_access_token(data={"sub": str(current_user.id), "email": current_user.email})
    refresh_token = create_refresh_token(data={"sub": str(current_user.id), "email": current_user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request a password reset token.
    In production, this would send an email. Here we return the token directly.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Return success even if user not found (prevents email enumeration)
        return {"message": "If that email exists, a reset link has been sent."}

    # Generate a 6-digit reset code
    reset_code = f"{secrets.randbelow(1000000):06d}"
    _reset_tokens[reset_code] = (user.email, datetime.utcnow() + timedelta(minutes=15))

    logger.info(f"Password reset code for {user.email}: {reset_code}")

    return {
        "message": "If that email exists, a reset link has been sent.",
        "reset_code": reset_code,  # In production, send via email instead
    }


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Reset password using a reset token/code.
    """
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    token_data = _reset_tokens.get(data.token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code"
        )

    email, expiry = token_data
    if datetime.utcnow() > expiry:
        _reset_tokens.pop(data.token, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset code has expired"
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    # Invalidate the used token
    _reset_tokens.pop(data.token, None)

    return {"message": "Password has been reset successfully"}
