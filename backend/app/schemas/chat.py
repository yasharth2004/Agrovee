"""
Chat Schemas
Pydantic models for chat and RAG chatbot
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# Chat Message
class ChatMessageCreate(BaseModel):
    """Create new chat message"""
    content: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[int] = None  # If None, creates new session
    context: Optional[dict] = None  # Optional context for RAG


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[str]
    created_at: datetime


# Chat Session
class ChatSessionCreate(BaseModel):
    """Create new chat session"""
    title: Optional[str] = "New Conversation"


class ChatSessionResponse(BaseModel):
    """Chat session response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    title: str
    is_active: bool
    message_count: int
    created_at: datetime
    updated_at: datetime


class ChatSessionDetail(ChatSessionResponse):
    """Chat session with messages"""
    messages: List[ChatMessageResponse]


# Chat List Response
class ChatSessionListResponse(BaseModel):
    """Paginated chat session list"""
    sessions: List[ChatSessionResponse]
    total: int
    page: int
    per_page: int


# RAG Response (includes retrieved context)
class RAGResponse(BaseModel):
    """RAG chatbot response with sources"""
    message: ChatMessageResponse
    retrieved_context: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None
