"""
Diagnosis Model
Stores crop disease diagnosis results, images, and AI predictions
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class DiagnosisStatus(str, enum.Enum):
    """Diagnosis processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Diagnosis(Base):
    """
    Diagnosis model
    Stores crop disease detection results and recommendations
    """
    __tablename__ = "diagnoses"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Image Information
    image_path = Column(Text, nullable=False)  # Path to uploaded image
    image_filename = Column(String(255), nullable=False)
    image_size = Column(Integer, nullable=True)  # Size in bytes
    
    # AI Prediction Results
    predicted_disease = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)
    crop_type = Column(String(100), nullable=True)  # Extracted from disease name
    
    # Model Information
    model_version = Column(String(50), nullable=True, default="1.0")
    all_predictions = Column(JSON, nullable=True)  # Top 5 predictions with probabilities
    
    # Explainability
    gradcam_path = Column(Text, nullable=True)  # Path to Grad-CAM visualization
    lime_explanation = Column(JSON, nullable=True)  # LIME feature importance
    
    # Weather & Environmental Data (for multimodal fusion)
    weather_data = Column(JSON, nullable=True)  # Temperature, humidity, etc.
    soil_type = Column(String(100), nullable=True)
    season = Column(String(50), nullable=True)
    
    # Multimodal Fusion Results
    fusion_confidence = Column(Float, nullable=True)  # Confidence after fusion
    risk_assessment = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Decision Engine Recommendations
    recommendations = Column(JSON, nullable=True)  # Fertilizer, pesticide, irrigation
    treatment_plan = Column(Text, nullable=True)
    estimated_yield_impact = Column(String(100), nullable=True)
    
    # Processing Status
    status = Column(SQLEnum(DiagnosisStatus), default=DiagnosisStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="diagnoses")
    
    def __repr__(self):
        return f"<Diagnosis(id={self.id}, disease={self.predicted_disease}, confidence={self.confidence_score})>"
    
    @property
    def is_healthy(self):
        """Check if crop is healthy"""
        return self.predicted_disease and "healthy" in self.predicted_disease.lower()
    
    @property
    def severity(self):
        """Get disease severity based on risk assessment"""
        severity_map = {
            "LOW": "Mild",
            "MEDIUM": "Moderate",
            "HIGH": "Severe",
            "CRITICAL": "Critical"
        }
        return severity_map.get(self.risk_assessment, "Unknown")
