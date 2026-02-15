"""
Multimodal Fusion Service
Combines image embeddings, weather data, and soil information
for enhanced disease prediction
"""

import numpy as np
from typing import Dict, Optional
import logging

# Try to import torch - run in demo mode if unavailable
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available - MultimodalFusionService using rule-based only")

logger = logging.getLogger(__name__)


if TORCH_AVAILABLE:
    class MultimodalFusionModel(nn.Module):
        """
        Neural network for fusing multiple modalities
        Combines vision embeddings with environmental features
        """
        
        def __init__(self, vision_dim=2048, weather_dim=4, soil_dim=10, hidden_dim=512, num_classes=38):
            super().__init__()
            
            # Feature projections
            self.vision_proj = nn.Sequential(
                nn.Linear(vision_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.3)
            )
            
            self.weather_proj = nn.Sequential(
                nn.Linear(weather_dim, 64),
                nn.ReLU()
            )
            
            self.soil_proj = nn.Sequential(
                nn.Linear(soil_dim, 64),
                nn.ReLU()
            )
            
            # Fusion layers
            fusion_dim = hidden_dim + 64 + 64
            self.fusion = nn.Sequential(
                nn.Linear(fusion_dim, 256),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Linear(128, num_classes)
            )
        
        def forward(self, vision_emb, weather_feat, soil_feat):
            """Forward pass through fusion network"""
            v = self.vision_proj(vision_emb)
            w = self.weather_proj(weather_feat)
            s = self.soil_proj(soil_feat)
            
            # Concatenate features
            fused = torch.cat([v, w, s], dim=1)
            
            # Final prediction
            output = self.fusion(fused)
            return output
else:
    MultimodalFusionModel = None


class MultimodalFusionService:
    """
    Service for multimodal disease prediction
    Enhances image-only predictions with environmental context
    """
    
    def __init__(self):
        self.model = None
        self.device = "cpu"
        self.soil_types = [
            "clay", "sandy", "loamy", "silty", "peaty", 
            "chalky", "saline", "laterite", "alluvial", "black"
        ]
        if TORCH_AVAILABLE:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize fusion model (untrained for now)"""
        if not TORCH_AVAILABLE or MultimodalFusionModel is None:
            logger.warning("⚠️ PyTorch not available - using rule-based fusion only")
            return
            
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = MultimodalFusionModel()
            self.model.to(self.device)
            self.model.eval()
            logger.info("✓ Multimodal fusion model initialized")
        except Exception as e:
            logger.error(f"Error initializing fusion model: {e}")
    
    def enhance_prediction(
        self,
        vision_prediction: Dict,
        weather_data: Optional[Dict],
        soil_type: Optional[str],
        season: Optional[str]
    ) -> Dict:
        """
        Enhance vision model prediction with environmental context
        
        Args:
            vision_prediction: Output from vision model
            weather_data: Weather features dictionary
            soil_type: Type of soil
            season: Current season
            
        Returns:
            Enhanced prediction with adjusted confidence and risk assessment
        """
        try:
            # Rule-based enhancement (since fusion model is not trained)
            enhanced = vision_prediction.copy()
            
            # Adjust confidence based on environmental factors
            confidence_adjustment = 1.0
            risk_factors = []
            
            # Weather-based adjustments
            if weather_data and "features" in weather_data:
                features = weather_data["features"]
                
                # High humidity increases disease risk
                if features["humidity_norm"] > 0.7:
                    confidence_adjustment *= 1.1
                    risk_factors.append("High humidity favorable for disease")
                
                # Rainfall increases fungal disease risk
                if features["rainfall_norm"] > 0.3:
                    if "mildew" in vision_prediction["predicted_disease"].lower() or \
                       "blight" in vision_prediction["predicted_disease"].lower():
                        confidence_adjustment *= 1.15
                        risk_factors.append("Recent rainfall increases fungal risk")
                
                # Extreme temperatures
                temp = weather_data["raw"]["temperature"]
                if temp > 35:
                    risk_factors.append("High temperature stress")
                elif temp < 10:
                    risk_factors.append("Low temperature stress")
            
            # Soil-based adjustments
            if soil_type:
                enhanced["soil_type"] = soil_type
                
                # Some diseases are more common in certain soil types
                if soil_type.lower() in ["clay", "poorly_drained"]:
                    if "rot" in vision_prediction["predicted_disease"].lower():
                        confidence_adjustment *= 1.1
                        risk_factors.append("Soil type conducive to root diseases")
            
            # Season-based adjustments
            if season:
                enhanced["season"] = season
                # Add seasonal risk factors (could be expanded)
                if season.lower() in ["monsoon", "rainy"]:
                    risk_factors.append("Rainy season increases disease spread")
            
            # Apply confidence adjustment (cap at reasonable range)
            original_confidence = vision_prediction["confidence"]
            adjusted_confidence = min(original_confidence * confidence_adjustment, 99.5)
            enhanced["fusion_confidence"] = round(adjusted_confidence, 2)
            enhanced["original_confidence"] = original_confidence
            
            # Risk assessment
            enhanced["risk_assessment"] = self._assess_risk(
                adjusted_confidence,
                vision_prediction["predicted_disease"],
                risk_factors
            )
            enhanced["risk_factors"] = risk_factors
            
            # Environmental context
            enhanced["environmental_context"] = {
                "weather_included": weather_data is not None,
                "soil_included": soil_type is not None,
                "season_included": season is not None
            }
            
            logger.info(f"Enhanced prediction: {original_confidence:.1f}% -> {adjusted_confidence:.1f}%")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in multimodal fusion: {e}")
            return vision_prediction
    
    def _assess_risk(self, confidence: float, disease: str, risk_factors: list) -> str:
        """
        Assess disease risk level
        
        Returns: LOW, MEDIUM, HIGH, or CRITICAL
        """
        # Check if healthy
        if "healthy" in disease.lower():
            return "LOW"
        
        # Base risk on confidence
        if confidence < 60:
            base_risk = "MEDIUM"
        elif confidence < 80:
            base_risk = "HIGH"
        else:
            base_risk = "CRITICAL"
        
        # Adjust based on number of risk factors
        if len(risk_factors) >= 2 and base_risk == "HIGH":
            base_risk = "CRITICAL"
        elif len(risk_factors) >= 3 and base_risk == "MEDIUM":
            base_risk = "HIGH"
        
        return base_risk
    
    def encode_soil_type(self, soil_type: Optional[str]) -> np.ndarray:
        """Encode soil type as one-hot vector"""
        soil_vector = np.zeros(len(self.soil_types))
        if soil_type and soil_type.lower() in self.soil_types:
            idx = self.soil_types.index(soil_type.lower())
            soil_vector[idx] = 1.0
        return soil_vector


# Global instance
_fusion_service = None

def get_fusion_service() -> MultimodalFusionService:
    """Get or create fusion service singleton"""
    global _fusion_service
    if _fusion_service is None:
        _fusion_service = MultimodalFusionService()
    return _fusion_service
