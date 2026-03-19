"""
Community Models
Posts, comments, and likes for the farmer community
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class CommunityPost(Base):
    """Community forum post"""
    __tablename__ = "community_posts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # pest_control, irrigation, etc.
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="community_posts")
    comments = relationship("CommunityComment", backref="post", cascade="all, delete-orphan")
    likes = relationship("CommunityLike", backref="post", cascade="all, delete-orphan")
    media = relationship("CommunityPostMedia", backref="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CommunityPost {self.id}>"


class CommunityComment(Base):
    """Comment on a community post"""
    __tablename__ = "community_comments"

    id = Column(String, primary_key=True, index=True)
    post_id = Column(String, ForeignKey("community_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="community_comments")

    def __repr__(self):
        return f"<CommunityComment {self.id}>"


class CommunityLike(Base):
    """Like on a community post"""
    __tablename__ = "community_likes"

    id = Column(String, primary_key=True, index=True)
    post_id = Column(String, ForeignKey("community_posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="community_likes")

    def __repr__(self):
        return f"<CommunityLike {self.id}>"


class CommunityPostMedia(Base):
    """Media attachments for community posts"""
    __tablename__ = "community_post_media"

    id = Column(String, primary_key=True, index=True)
    post_id = Column(String, ForeignKey("community_posts.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    mime_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CommunityPostMedia {self.id}>"
