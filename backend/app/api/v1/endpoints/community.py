"""
Community Endpoints
Posts, comments, and interactions for farmer community
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
import uuid
from datetime import datetime
import logging
from pathlib import Path

from app.db.session import get_db
from app.models.user import User
from app.models.community import (
    CommunityPost,
    CommunityComment,
    CommunityLike,
    CommunityPostMedia,
)
from app.schemas.community import (
    CommunityPostCreate,
    CommunityPostResponse,
    CommunityPostDetailResponse,
    CommunityCommentCreate,
    CommunityCommentResponse,
    CommunityMediaResponse,
)
from app.core.security import get_current_user
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
MEDIA_ROOT = Path(settings.UPLOAD_DIR) / "community"


def _build_media_payload(media_items: List[CommunityPostMedia]) -> List[CommunityMediaResponse]:
    payload = []
    for media in media_items or []:
        payload.append(
            CommunityMediaResponse(
                id=media.id,
                file_name=media.file_name,
                url=media.file_url,
                mime_type=media.mime_type,
            )
        )
    return payload


def _serialize_post(
    post: CommunityPost,
    likes_count: int,
    comments_count: int,
    is_liked: bool,
):
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "views": post.views,
        "views_count": post.views,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "is_liked": is_liked,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "media": _build_media_payload(post.media),
    }


async def _save_post_media(
    files: List[UploadFile],
    post_id: str,
    db: Session,
):
    if not files:
        return []

    saved_media: List[CommunityPostMedia] = []
    allowed_types = set(settings.ALLOWED_IMAGE_TYPES)

    for upload in files:
        if not upload or not upload.filename:
            continue

        if upload.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {upload.content_type}",
            )

        file_bytes = await upload.read()
        if len(file_bytes) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 10MB.",
            )

        file_extension = Path(upload.filename).suffix or ".jpg"
        safe_name = f"{uuid.uuid4().hex}{file_extension}"
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        destination = MEDIA_ROOT / safe_name

        with open(destination, "wb") as buffer:
            buffer.write(file_bytes)

        media = CommunityPostMedia(
            id=str(uuid.uuid4()),
            post_id=post_id,
            file_name=upload.filename,
            file_path=str(destination),
            file_url=f"/uploads/community/{safe_name}",
            mime_type=upload.content_type or "image/jpeg",
        )
        db.add(media)
        saved_media.append(media)

        await upload.close()

    if saved_media:
        db.commit()
        for media in saved_media:
            db.refresh(media)

    return saved_media


def _cleanup_media_files(media_items: List[CommunityPostMedia]):
    for media in media_items or []:
        if not media.file_path:
            continue
        file_path = Path(media.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as exc:
                logger.warning("Failed to remove media file %s: %s", media.file_path, exc)


@router.post("/posts", response_model=CommunityPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new community post with optional media"""
    # Validate payload using schema
    CommunityPostCreate(title=title, content=content, category=category)

    post = CommunityPost(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=title,
        content=content,
        category=category,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    saved_media = await _save_post_media(images, post.id, db)
    if saved_media:
        post.media = saved_media

    return _serialize_post(post, likes_count=0, comments_count=0, is_liked=False)


@router.get("/posts", response_model=List[CommunityPostResponse])
async def list_posts(
    category: str = Query("all", description="Filter by category"),
    search: str = Query("", description="Search posts"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List community posts with optional filtering and search"""
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
    
    # Order by newest first
    posts = query.order_by(desc(CommunityPost.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        likes_count = db.query(func.count(CommunityLike.id)).filter(CommunityLike.post_id == post.id).scalar() or 0
        comments_count = len(post.comments)
        is_liked = db.query(CommunityLike).filter(
            CommunityLike.post_id == post.id,
            CommunityLike.user_id == current_user.id
        ).first() is not None

        result.append(
            _serialize_post(
                post,
                likes_count=likes_count,
                comments_count=comments_count,
                is_liked=is_liked,
            )
        )

    return result


@router.get("/posts/{post_id}", response_model=CommunityPostDetailResponse)
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single community post with comments"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Increment view count
    post.views += 1
    db.commit()
    db.refresh(post)
    
    likes_count = db.query(func.count(CommunityLike.id)).filter(CommunityLike.post_id == post.id).scalar() or 0
    is_liked = db.query(CommunityLike).filter(
        CommunityLike.post_id == post.id,
        CommunityLike.user_id == current_user.id
    ).first() is not None
    
    comments = [
        {
            "id": c.id,
            "content": c.content,
            "user_id": c.user_id,
            "created_at": c.created_at,
        }
        for c in post.comments
    ]

    response_payload = _serialize_post(
        post,
        likes_count=likes_count,
        comments_count=len(post.comments),
        is_liked=is_liked,
    )
    response_payload["comments"] = comments
    return response_payload


@router.post("/posts/{post_id}/comments", response_model=CommunityCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: str,
    comment_data: CommunityCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a post"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comment = CommunityComment(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {
        "id": comment.id,
        "content": comment.content,
        "user_id": comment.user_id,
        "created_at": comment.created_at,
    }


@router.delete("/posts/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment"""
    comment = db.query(CommunityComment).filter(CommunityComment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    db.delete(comment)
    db.commit()


@router.post("/posts/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if already liked
    existing_like = db.query(CommunityLike).filter(
        CommunityLike.post_id == post_id,
        CommunityLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    like = CommunityLike(
        id=str(uuid.uuid4()),
        post_id=post_id,
        user_id=current_user.id,
    )
    db.add(like)
    db.commit()
    
    return {"message": "Post liked"}


@router.delete("/posts/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    like = db.query(CommunityLike).filter(
        CommunityLike.post_id == post_id,
        CommunityLike.user_id == current_user.id
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    db.delete(like)
    db.commit()


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only by author)"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    media_to_remove = list(post.media)
    db.delete(post)
    db.commit()
    _cleanup_media_files(media_to_remove)
