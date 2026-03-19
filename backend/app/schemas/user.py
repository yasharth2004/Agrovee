"""
User Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


# Base User Schema
class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[str] = None


# User Registration
class UserRegister(UserBase):
    """User registration request"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str


# User Login
class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


# Token Response
class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str


# User Update
class UserUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[str] = None
    profile_picture_url: Optional[str] = None


# Password Change
class PasswordChange(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


# Password Reset
class PasswordResetRequest(BaseModel):
    """Request password reset token"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


# User Response (Public)
class UserResponse(UserBase):
    """User response (public information)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_verified: bool
    profile_picture_url: Optional[str]
    created_at: datetime
    diagnosis_count: int = 0


# User Profile (Private - includes more details)
class UserProfile(UserResponse):
    """User profile (private information for owner)"""
    last_login: Optional[datetime]
    updated_at: datetime


# Admin User Response (includes admin fields)
class UserAdmin(UserProfile):
    """User response for admins"""
    is_admin: bool
    hashed_password: str  # Only for debugging, never expose in API


# User List Response
class UserListResponse(BaseModel):
    """Paginated user list response"""
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
