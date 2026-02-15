"""
Diagnosis Endpoints
Image upload, disease detection, history
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import os
import uuid
from datetime import datetime
import logging

from app.db.session import get_db
from app.models.user import User
from app.models.diagnosis import Diagnosis, DiagnosisStatus
from app.schemas.diagnosis import (
    DiagnosisResponse,
    DiagnosisSummary,
    DiagnosisListResponse,
    DiagnosisRequest
)
from app.core.security import get_current_user
from app.core.config import settings
from app.services import (
    get_vision_service,
    get_weather_service,
    get_fusion_service,
    get_decision_engine
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/diagnose", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    image: UploadFile = File(...),
    soil_type: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload image for disease diagnosis
    
    - **image**: Crop image file (JPG, PNG)
    - **soil_type**: Optional soil type
    - **location**: Optional location for weather data
    - **season**: Optional season information
    
    Returns diagnosis ID for tracking
    Processing happens asynchronously
    """
    # Validate file type
    if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Validate file size
    contents = await image.read()
    file_size = len(contents)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Create upload directory if not exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create diagnosis record
    diagnosis = Diagnosis(
        user_id=current_user.id,
        image_path=file_path,
        image_filename=image.filename,
        image_size=file_size,
        soil_type=soil_type,
        season=season,
        status=DiagnosisStatus.PENDING
    )
    
    db.add(diagnosis)
    db.commit()
    db.refresh(diagnosis)
    
    # Process with AI (synchronous for now)
    # In production, use background task or Celery
    try:
        await process_diagnosis(diagnosis.id, location, db)
    except Exception as e:
        logger.error(f"Error processing diagnosis {diagnosis.id}: {e}")
        # Don't fail the request - diagnosis record is saved
        diagnosis.status = DiagnosisStatus.FAILED
        db.commit()
    
    db.refresh(diagnosis)
    return diagnosis


@router.get("/diagnose/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get diagnosis result by ID
    """
    diagnosis = db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
        Diagnosis.user_id == current_user.id
    ).first()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    return diagnosis


@router.get("/history", response_model=DiagnosisListResponse)
async def get_diagnosis_history(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's diagnosis history with pagination
    """
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    total = db.query(Diagnosis).filter(Diagnosis.user_id == current_user.id).count()
    
    # Get diagnoses
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.user_id == current_user.id
    ).order_by(desc(Diagnosis.created_at)).offset(offset).limit(per_page).all()
    
    return {
        "diagnoses": diagnoses,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.delete("/diagnose/{diagnosis_id}")
async def delete_diagnosis(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a diagnosis record
    """
    diagnosis = db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
        Diagnosis.user_id == current_user.id
    ).first()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    # Delete image file
    if os.path.exists(diagnosis.image_path):
        os.remove(diagnosis.image_path)
    
    # Delete Grad-CAM if exists
    if diagnosis.gradcam_path and os.path.exists(diagnosis.gradcam_path):
        os.remove(diagnosis.gradcam_path)
    
    # Delete record
    db.delete(diagnosis)
    db.commit()
    
    return {
        "success": True,
        "message": "Diagnosis deleted successfully"
    }


@router.get("/recent")
async def get_recent_diagnoses(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent diagnoses (for dashboard)
    """
    diagnoses = db.query(Diagnosis).filter(
        Diagnosis.user_id == current_user.id
    ).order_by(desc(Diagnosis.created_at)).limit(limit).all()
    
    return diagnoses


async def process_diagnosis(diagnosis_id: int, location: Optional[str], db: Session):
    """
    Process diagnosis with AI services
    
    Steps:
    1. Run vision model on image
    2. Fetch weather data
    3. Apply multimodal fusion
    4. Generate recommendations
    5. Update diagnosis record
    """
    try:
        # Get diagnosis record
        diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if not diagnosis:
            logger.error(f"Diagnosis {diagnosis_id} not found")
            return
        
        diagnosis.status = DiagnosisStatus.PROCESSING
        db.commit()
        
        logger.info(f"Processing diagnosis {diagnosis_id}: {diagnosis.image_path}")
        
        # Step 1: Vision model inference
        vision_service = get_vision_service()
        vision_result = vision_service.predict(diagnosis.image_path, diagnosis.image_filename or "")
        
        logger.info(f"Vision prediction: {vision_result['predicted_disease']} ({vision_result['confidence']:.1f}%)")
        
        # Step 2: Fetch weather data
        weather_data = None
        if location:
            try:
                weather_service = get_weather_service()
                weather_data = weather_service.get_weather_features(location)
                logger.info(f"Weather fetched for {location}: {weather_data['raw']['temperature']}°C")
            except Exception as e:
                logger.warning(f"Weather fetch failed: {e}")
        
        # Step 3: Multimodal fusion
        fusion_service = get_fusion_service()
        enhanced_prediction = fusion_service.enhance_prediction(
            vision_result,
            weather_data,
            diagnosis.soil_type,
            diagnosis.season
        )
        
        logger.info(f"Fusion confidence: {enhanced_prediction['fusion_confidence']:.1f}% (risk: {enhanced_prediction['risk_assessment']})")
        
        # Step 4: Generate recommendations
        decision_engine = get_decision_engine()
        recommendations = decision_engine.generate_recommendations(
            disease=enhanced_prediction["predicted_disease"],
            crop=enhanced_prediction["crop_type"],
            confidence=enhanced_prediction["fusion_confidence"],
            risk_level=enhanced_prediction["risk_assessment"],
            weather_data=weather_data,
            soil_type=diagnosis.soil_type
        )
        
        logger.info(f"Generated {len(recommendations['treatments'])} treatment recommendations")
        
        # Step 5: Update diagnosis record
        diagnosis.predicted_disease = enhanced_prediction["predicted_disease"]
        diagnosis.confidence_score = enhanced_prediction["confidence"]
        diagnosis.fusion_confidence = enhanced_prediction["fusion_confidence"]
        diagnosis.all_predictions = vision_result["top_predictions"]
        diagnosis.crop_type = enhanced_prediction["crop_type"]
        diagnosis.weather_data = weather_data["raw"] if weather_data else None
        diagnosis.risk_assessment = enhanced_prediction["risk_assessment"]
        diagnosis.recommendations = recommendations
        diagnosis.status = DiagnosisStatus.COMPLETED
        diagnosis.processed_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"✓ Diagnosis {diagnosis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in process_diagnosis: {e}", exc_info=True)
        # Update status to failed
        diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
        if diagnosis:
            diagnosis.status = DiagnosisStatus.FAILED
            db.commit()
        raise
