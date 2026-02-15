"""
User Profile Endpoints
Profile management, update, statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.diagnosis import Diagnosis
from app.schemas.user import UserResponse, UserProfile, UserUpdate, PasswordChange
from app.core.security import (
    get_current_user,
    get_password_hash,
    verify_password
)

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's detailed profile
    """
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    """
    # Update fields
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    if profile_data.location is not None:
        current_user.location = profile_data.location
    if profile_data.farm_size is not None:
        current_user.farm_size = profile_data.farm_size
    if profile_data.profile_picture_url is not None:
        current_user.profile_picture_url = profile_data.profile_picture_url
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics
    Returns diagnosis counts, common diseases, etc.
    """
    # Total diagnoses
    total_diagnoses = db.query(func.count(Diagnosis.id)).filter(
        Diagnosis.user_id == current_user.id
    ).scalar()
    
    # Healthy vs diseased
    healthy_count = db.query(func.count(Diagnosis.id)).filter(
        Diagnosis.user_id == current_user.id,
        Diagnosis.predicted_disease.ilike("%healthy%")
    ).scalar()
    
    diseased_count = total_diagnoses - healthy_count
    
    # Most common disease
    most_common = db.query(
        Diagnosis.predicted_disease,
        func.count(Diagnosis.id).label("count")
    ).filter(
        Diagnosis.user_id == current_user.id,
        ~Diagnosis.predicted_disease.ilike("%healthy%")
    ).group_by(
        Diagnosis.predicted_disease
    ).order_by(
        func.count(Diagnosis.id).desc()
    ).first()
    
    # Average confidence
    avg_confidence = db.query(func.avg(Diagnosis.confidence_score)).filter(
        Diagnosis.user_id == current_user.id
    ).scalar() or 0.0
    
    # Recent diagnoses
    recent = db.query(Diagnosis).filter(
        Diagnosis.user_id == current_user.id
    ).order_by(Diagnosis.created_at.desc()).limit(5).all()
    
    return {
        "total_diagnoses": total_diagnoses,
        "healthy_count": healthy_count,
        "diseased_count": diseased_count,
        "most_common_disease": most_common[0] if most_common else None,
        "average_confidence": round(float(avg_confidence), 2),
        "recent_diagnoses": recent
    }


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account (soft delete - deactivate)
    """
    current_user.is_active = False
    db.commit()
    
    return {
        "success": True,
        "message": "Account deactivated successfully"
    }
