"""
Chat Endpoints
RAG chatbot conversations and messages
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import json
import logging

from app.db.session import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionDetail,
    ChatSessionListResponse
)
from app.core.security import get_current_user
from app.services import get_chatbot_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the chatbot
    
    - If session_id is provided, adds to existing session
    - If session_id is None, creates a new session
    
    Returns assistant response with RAG context
    """
    # Get or create session
    if message_data.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == message_data.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
    else:
        # Create new session
        session = ChatSession(
            user_id=current_user.id,
            title=message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    
    # Process with RAG chatbot
    try:
        chatbot_service = get_chatbot_service()
        
        # Build context from conversation history
        context = {}
        if message_data.context:
            context = message_data.context
        
        # Get RAG response
        response = chatbot_service.chat(message_data.content, context)
        
        assistant_response = response["answer"]
        sources = [source["id"] for source in response["sources"]]
        retrieved_docs = response.get("retrieved_docs", [])
        
        logger.info(f"RAG response generated with {len(sources)} sources")
        
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        assistant_response = "I apologize, but I'm having trouble processing your question. Please try again."
        sources = []
        retrieved_docs = []
    
    # Save assistant message
    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_response,
        sources=", ".join(sources) if sources else None,
        retrieved_docs=json.dumps(retrieved_docs) if retrieved_docs else None
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    return assistant_message


@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_chat_sessions(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's chat sessions with pagination
    """
    offset = (page - 1) * per_page
    
    # Get total count
    total = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).count()
    
    # Get sessions
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(desc(ChatSession.updated_at)).offset(offset).limit(per_page).all()
    
    return {
        "sessions": sessions,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat session with all messages
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all its messages
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {
        "success": True,
        "message": "Chat session deleted successfully"
    }


@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: int,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update chat session title
    """
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    session.title = title
    db.commit()
    
    return {
        "success": True,
        "message": "Session title updated"
    }
