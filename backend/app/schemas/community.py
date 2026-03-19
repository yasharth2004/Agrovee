"""
Community Schemas
Request/response schemas for community endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CommunityCommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str = Field(..., min_length=1, max_length=2000)


class CommunityCommentResponse(BaseModel):
    """Schema for comment response"""
    id: str
    content: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommunityPostCreate(BaseModel):
    """Schema for creating a post"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=5000)
    category: str = Field(..., min_length=1, max_length=50)


class CommunityMediaResponse(BaseModel):
    """Schema for post media attachments"""
    id: str
    file_name: str
    url: str
    mime_type: str

    class Config:
        from_attributes = True


class CommunityPostResponse(BaseModel):
    """Schema for post response"""
    id: str
    title: str
    content: str
    category: str
    views: int = 0
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime
    media: List[CommunityMediaResponse] = []

    class Config:
        from_attributes = True


class CommunityPostDetailResponse(CommunityPostResponse):
    """Schema for detailed post response with comments"""
    comments: List[CommunityCommentResponse] = []
