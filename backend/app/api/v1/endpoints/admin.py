"""
Admin Endpoints
Moderation and system administration endpoints
Only accessible by admin users
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.community import CommunityPost, CommunityComment, CommunityLike
from app.core.security import get_current_user
from pathlib import Path
from app.core.config import settings

router = APIRouter()


def _check_admin(user: User):
    """Check if user is admin"""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def _cleanup_media_files(post: CommunityPost):
    """Delete associated media files"""
    for media in post.media or []:
        if not media.file_path:
            continue
        file_path = Path(media.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as exc:
                print(f"Failed to remove media file {media.file_path}: {exc}")


# Admin Dashboard Stats
@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    _check_admin(current_user)
    
    # Count stats
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_posts = db.query(func.count(CommunityPost.id)).scalar() or 0
    total_comments = db.query(func.count(CommunityComment.id)).scalar() or 0
    
    # Get posts by category
    category_stats = db.query(
        CommunityPost.category,
        func.count(CommunityPost.id).label("count")
    ).group_by(CommunityPost.category).all()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_posts": total_posts,
        "total_comments": total_comments,
        "posts_by_category": [
            {"category": cat, "count": count}
            for cat, count in category_stats
        ]
    }


# Community Post Moderation
@router.get("/community/posts")
async def list_all_posts(
    category: str = Query("all", description="Filter by category"),
    search: str = Query("", description="Search posts"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("recent", description="Sort by: recent, oldest, popular"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all community posts (admin only)
    Allows filtering, searching, and different sort options
    """
    _check_admin(current_user)
    
    query = db.query(CommunityPost)
    
    # Filter by category
    if category and category != "all":
        query = query.filter(CommunityPost.category == category)
    
    # Search in title and content
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (CommunityPost.title.ilike(search_term)) |
            (CommunityPost.content.ilike(search_term))
        )
    
    # Sort
    if sort_by == "oldest":
        query = query.order_by(CommunityPost.created_at.asc())
    elif sort_by == "popular":
        query = query.order_by(desc(CommunityPost.views))
    else:  # recent (default)
        query = query.order_by(desc(CommunityPost.created_at))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    posts = query.offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        likes_count = db.query(func.count(CommunityLike.id)).filter(
            CommunityLike.post_id == post.id
        ).scalar() or 0
        comments_count = len(post.comments)
        
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "views": post.views,
            "likes_count": likes_count,
            "comments_count": comments_count,
            "user_id": post.user_id,
            "user_email": post.user.email,
            "user_name": post.user.full_name or post.user.email,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "media_count": len(post.media) if post.media else 0
        })
    
    return {
        "posts": result,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit
    }


@router.get("/community/posts/{post_id}")
async def get_post_details(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed view of a community post (admin only)"""
    _check_admin(current_user)
    
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    likes_count = db.query(func.count(CommunityLike.id)).filter(
        CommunityLike.post_id == post.id
    ).scalar() or 0
    
    comments = [
        {
            "id": c.id,
            "content": c.content,
            "user_id": c.user_id,
            "user_email": c.user.email,
            "user_name": c.user.full_name or c.user.email,
            "created_at": c.created_at,
        }
        for c in post.comments
    ]
    
    media = [
        {
            "id": m.id,
            "file_name": m.file_name,
            "file_url": m.file_url,
            "mime_type": m.mime_type,
            "created_at": m.created_at
        }
        for m in post.media
    ]
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "views": post.views,
        "likes_count": likes_count,
        "comments_count": len(post.comments),
        "user_id": post.user_id,
        "user_email": post.user.email,
        "user_name": post.user.full_name or post.user.email,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "comments": comments,
        "media": media
    }


@router.delete("/community/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post_admin(
    post_id: str,
    reason: str = Query("", description="Reason for deletion"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a community post (admin only)"""
    _check_admin(current_user)
    
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    deleted_by_email = current_user.email
    post_title = post.title
    post_author = post.user.email
    media_to_remove = list(post.media)
    
    db.delete(post)
    db.commit()
    _cleanup_media_files(media_to_remove)
    
    return {
        "message": "Post deleted successfully",
        "deleted_post_id": post_id,
        "deleted_post_title": post_title,
        "post_author": post_author,
        "deleted_by": deleted_by_email,
        "reason": reason,
        "timestamp": datetime.utcnow()
    }


@router.delete("/community/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment_admin(
    comment_id: str,
    reason: str = Query("", description="Reason for deletion"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a community comment (admin only)"""
    _check_admin(current_user)
    
    comment = db.query(CommunityComment).filter(CommunityComment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    deleted_by_email = current_user.email
    comment_author = comment.user.email
    
    db.delete(comment)
    db.commit()
    
    return {
        "message": "Comment deleted successfully",
        "deleted_comment_id": comment_id,
        "comment_author": comment_author,
        "deleted_by": deleted_by_email,
        "reason": reason,
        "timestamp": datetime.utcnow()
    }


# User Management
@router.get("/users")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Search by email or name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    _check_admin(current_user)
    
    query = db.query(User)
    
    # Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) |
            (User.full_name.ilike(search_term))
        )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "is_verified": u.is_verified,
                "created_at": u.created_at,
                "last_login": u.last_login
            }
            for u in users
        ],
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit
    }


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate/deactivate a user account (admin only)"""
    _check_admin(current_user)
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user_id": user_id,
        "is_active": user.is_active
    }
