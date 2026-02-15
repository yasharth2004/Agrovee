"""
Diagnosis Schemas
Pydantic models for diagnosis requests and responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DiagnosisStatusEnum(str, Enum):
    """Diagnosis processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Diagnosis Request
class DiagnosisRequest(BaseModel):
    """Diagnosis creation request with optional environmental data"""
    soil_type: Optional[str] = Field(None, description="Soil type (clay, sandy, loamy, etc.)")
    location: Optional[str] = Field(None, description="Location for weather data")
    season: Optional[str] = Field(None, description="Current season")
    additional_notes: Optional[str] = None


# Weather Data
class WeatherData(BaseModel):
    """Weather information"""
    temperature: Optional[float] = None  # Celsius
    humidity: Optional[float] = None  # Percentage
    rainfall: Optional[float] = None  # mm
    wind_speed: Optional[float] = None  # km/h
    description: Optional[str] = None


# Prediction Result
class PredictionResult(BaseModel):
    """Single prediction result"""
    disease_name: str
    probability: float
    crop_type: str


# Recommendations
class Recommendations(BaseModel):
    """Treatment recommendations"""
    fertilizer: Optional[str] = None
    pesticide: Optional[str] = None
    irrigation: Optional[str] = None
    additional_care: Optional[List[str]] = None


# Diagnosis Response
class DiagnosisResponse(BaseModel):
    """Complete diagnosis response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    
    # Image info
    image_filename: str
    image_path: str
    
    # Predictions
    predicted_disease: Optional[str]
    confidence_score: Optional[float]
    crop_type: Optional[str]
    all_predictions: Optional[List[Dict[str, Any]]]
    
    # Environmental
    weather_data: Optional[Dict[str, Any]]
    soil_type: Optional[str]
    season: Optional[str]
    
    # Results
    fusion_confidence: Optional[float]
    risk_assessment: Optional[str]
    recommendations: Optional[Dict[str, Any]]
    treatment_plan: Optional[str]
    
    # Explainability
    gradcam_path: Optional[str]
    
    # Status
    status: str
    error_message: Optional[str]
    
    # Timestamps
    created_at: datetime
    processed_at: Optional[datetime]


# Diagnosis Summary (for history list)
class DiagnosisSummary(BaseModel):
    """Diagnosis summary for list view"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    predicted_disease: Optional[str]
    confidence_score: Optional[float]
    crop_type: Optional[str]
    risk_assessment: Optional[str]
    status: str
    created_at: datetime


# Diagnosis List Response
class DiagnosisListResponse(BaseModel):
    """Paginated diagnosis list"""
    diagnoses: List[DiagnosisSummary]
    total: int
    page: int
    per_page: int


# Statistics Response
class DiagnosisStats(BaseModel):
    """User diagnosis statistics"""
    total_diagnoses: int
    healthy_count: int
    diseased_count: int
    most_common_disease: Optional[str]
    average_confidence: float
    recent_diagnoses: List[DiagnosisSummary]
