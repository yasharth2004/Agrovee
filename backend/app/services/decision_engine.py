"""
Decision Engine Service
Generates actionable recommendations based on disease diagnosis
and environmental factors
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DecisionEngineService:
    """
    Service for generating treatment recommendations
    Combines ML predictions with domain knowledge rules
    """
    
    def __init__(self):
        # Knowledge base of treatments
        self.treatments = self._load_treatment_knowledge()
        
        # Fertilizer recommendations by crop
        self.fertilizer_guide = self._load_fertilizer_guide()
        
        # Pesticide/fungicide database
        self.pesticide_guide = self._load_pesticide_guide()
    
    def generate_recommendations(
        self,
        disease: str,
        crop: str,
        confidence: float,
        risk_level: str,
        weather_data: Optional[Dict],
        soil_type: Optional[str]
    ) -> Dict:
        """
        Generate comprehensive treatment recommendations
        
        Returns:
            Dictionary with immediate actions, treatments, and preventive measures
        """
        try:
            recommendations = {
                "disease": disease,
                "crop": crop,
                "risk_level": risk_level,
                "immediate_actions": [],
                "treatments": [],
                "fertilizer_recommendations": [],
                "irrigation_guidance": [],
                "preventive_measures": [],
                "monitoring_schedule": {},
                "cost_estimate": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if healthy
            if "healthy" in disease.lower():
                return self._healthy_recommendations(crop, weather_data, soil_type)
            
            # Get disease-specific treatment
            disease_key = self._normalize_disease_name(disease)
            treatment = self.treatments.get(disease_key, self._get_generic_treatment(disease))
            
            # Immediate actions based on risk level
            if risk_level == "CRITICAL":
                recommendations["immediate_actions"] = [
                    "🚨 Isolate affected plants immediately to prevent spread",
                    "Remove and destroy severely infected plant parts",
                    "Apply recommended treatment within 24 hours",
                    "Monitor neighboring plants daily"
                ]
            elif risk_level == "HIGH":
                recommendations["immediate_actions"] = [
                    "⚠️ Remove affected leaves/stems carefully",
                    "Apply treatment within 2-3 days",
                    "Increase monitoring frequency"
                ]
            else:
                recommendations["immediate_actions"] = [
                    "Monitor plant condition daily",
                    "Prepare treatment materials",
                    "Check surrounding plants"
                ]
            
            # Chemical/organic treatments
            recommendations["treatments"] = treatment["treatments"]
            
            # Fertilizer recommendations
            recommendations["fertilizer_recommendations"] = self._get_fertilizer_recommendations(
                crop, disease, soil_type
            )
            
            # Irrigation guidance based on weather and disease
            recommendations["irrigation_guidance"] = self._get_irrigation_guidance(
                disease, weather_data
            )
            
            # Preventive measures
            recommendations["preventive_measures"] = treatment.get("prevention", [
                "Maintain proper plant spacing",
                "Ensure good air circulation",
                "Regular field inspection",
                "Practice crop rotation"
            ])
            
            # Monitoring schedule
            recommendations["monitoring_schedule"] = {
                "frequency": "Daily for 7 days, then every 3 days" if risk_level in ["HIGH", "CRITICAL"] else "Every 3-5 days",
                "key_indicators": [
                    "Spread to new leaves/plants",
                    "Color changes",
                    "Growth rate",
                    "New spots or lesions"
                ]
            }
            
            # Cost estimate
            recommendations["cost_estimate"] = self._estimate_treatment_cost(
                disease, crop, risk_level
            )
            
            logger.info(f"Generated recommendations for {disease} ({risk_level})")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._get_generic_recommendations(disease, crop)
    
    def _normalize_disease_name(self, disease: str) -> str:
        """Normalize disease name for lookup"""
        # Convert "Tomato___Early_Blight" to "early_blight"
        if "___" in disease:
            disease = disease.split("___")[1]
        return disease.lower().replace("_", " ").strip()
    
    def _load_treatment_knowledge(self) -> Dict:
        """Load disease treatment knowledge base"""
        return {
            "early blight": {
                "treatments": [
                    {
                        "type": "Fungicide",
                        "name": "Chlorothalonil",
                        "application": "Spray every 7-10 days",
                        "dosage": "2-3 ml per liter of water",
                        "organic_alternative": "Neem oil (5ml/liter water)"
                    },
                    {
                        "type": "Organic",
                        "name": "Copper-based fungicide",
                        "application": "Spray weekly",
                        "dosage": "As per manufacturer instructions"
                    }
                ],
                "prevention": [
                    "Remove infected leaves immediately",
                    "Avoid overhead watering",
                    "Improve air circulation",
                    "Apply mulch to prevent soil splash"
                ]
            },
            "late blight": {
                "treatments": [
                    {
                        "type": "Fungicide",
                        "name": "Mancozeb or Metalaxyl",
                        "application": "Spray every 5-7 days during infection",
                        "dosage": "Follow label instructions",
                        "warning": "Act quickly - this disease spreads rapidly"
                    }
                ],
                "prevention": [
                    "Remove all infected plant material",
                    "Ensure excellent drainage",
                    "Avoid planting in humid, cool conditions"
                ]
            },
            "powdery mildew": {
                "treatments": [
                    {
                        "type": "Fungicide",
                        "name": "Sulfur-based spray",
                        "application": "Weekly application",
                        "organic_alternative": "Baking soda solution (1 tbsp/gallon water)"
                    },
                    {
                        "type": "Organic",
                        "name": "Milk spray",
                        "application": "40% milk, 60% water mix, spray weekly",
                        "effectiveness": "Proven effective for mild infections"
                    }
                ],
                "prevention": [
                    "Prune for better air circulation",
                    "Water at soil level, not leaves",
                    "Plant resistant varieties"
                ]
            },
            "leaf spot": {
                "treatments": [
                    {
                        "type": "Fungicide",
                        "name": "Copper fungicide",
                        "application": "Spray every 7-14 days",
                        "organic_alternative": "Neem oil"
                    }
                ],
                "prevention": [
                    "Remove fallen leaves",
                    "Avoid wetting foliage",
                    "Space plants properly"
                ]
            },
            "bacterial spot": {
                "treatments": [
                    {
                        "type": "Bactericide",
                        "name": "Copper-based spray",
                        "application": "Weekly application",
                        "note": "More difficult to control than fungal diseases"
                    }
                ],
                "prevention": [
                    "Use disease-free seeds",
                    "Practice crop rotation (3-year cycle)",
                    "Remove infected plants completely",
                    "Disinfect tools between plants"
                ]
            }
        }
    
    def _get_generic_treatment(self, disease: str) -> Dict:
        """Provide generic treatment for unknown diseases"""
        disease_type = "fungal"  # Default assumption
        
        if "bacterial" in disease.lower():
            disease_type = "bacterial"
        elif "virus" in disease.lower() or "mosaic" in disease.lower():
            disease_type = "viral"
        
        if disease_type == "bacterial":
            return {
                "treatments": [
                    {
                        "type": "Bactericide",
                        "name": "Copper-based spray",
                        "application": "Apply weekly"
                    }
                ],
                "prevention": ["Remove infected plants", "Disinfect tools", "Improve drainage"]
            }
        elif disease_type == "viral":
            return {
                "treatments": [
                    {
                        "type": "Management",
                        "name": "No chemical cure available",
                        "application": "Remove infected plants to prevent spread",
                        "note": "Control insect vectors (aphids, whiteflies)"
                    }
                ],
                "prevention": ["Use resistant varieties", "Control insect vectors", "Remove infected plants immediately"]
            }
        else:  # Fungal
            return {
                "treatments": [
                    {
                        "type": "Fungicide",
                        "name": "Broad-spectrum fungicide",
                        "application": "Apply as per product instructions",
                        "organic_alternative": "Neem oil or copper spray"
                    }
                ],
                "prevention": ["Improve air circulation", "Avoid overhead watering", "Remove infected material"]
            }
    
    def _load_fertilizer_guide(self) -> Dict:
        """Load fertilizer recommendations by crop"""
        return {
            "tomato": {
                "npk_ratio": "5-10-10",
                "frequency": "Every 2 weeks during growing season",
                "organic_options": ["Compost", "Fish emulsion", "Bone meal"]
            },
            "potato": {
                "npk_ratio": "10-10-20",
                "frequency": "At planting and mid-season",
                "organic_options": ["Compost", "Wood ash (potassium)"]
            },
            "pepper": {
                "npk_ratio": "5-10-10",
                "frequency": "Every 2-3 weeks",
                "organic_options": ["Compost tea", "Worm castings"]
            },
            "general": {
                "npk_ratio": "10-10-10 (balanced)",
                "frequency": "Every 3-4 weeks",
                "organic_options": ["Compost", "Manure", "Green manure"]
            }
        }
    
    def _load_pesticide_guide(self) -> Dict:
        """Load pesticide/fungicide database"""
        # Could be expanded significantly
        return {}
    
    def _get_fertilizer_recommendations(self, crop: str, disease: str, soil_type: Optional[str]) -> List[Dict]:
        """Get fertilizer recommendations"""
        crop_lower = crop.lower()
        guide = self.fertilizer_guide.get(crop_lower, self.fertilizer_guide["general"])
        
        recommendations = [
            {
                "type": "NPK Fertilizer",
                "ratio": guide["npk_ratio"],
                "frequency": guide["frequency"],
                "application_method": "Side dressing or diluted in water"
            }
        ]
        
        # Add organic options
        for organic in guide["organic_options"]:
            recommendations.append({
                "type": "Organic",
                "name": organic,
                "frequency": "Monthly",
                "benefits": "Improves soil health and microbial activity"
            })
        
        return recommendations
    
    def _get_irrigation_guidance(self, disease: str, weather_data: Optional[Dict]) -> List[str]:
        """Get irrigation recommendations based on disease and weather"""
        guidance = []
        
        # Disease-specific irrigation
        if "blight" in disease.lower() or "mildew" in disease.lower():
            guidance.append("🚰 Reduce watering frequency - fungal diseases thrive in moisture")
            guidance.append("Water at soil level, avoid wetting leaves")
            guidance.append("Water in early morning to allow foliage to dry")
        elif "wilt" in disease.lower():
            guidance.append("Maintain consistent soil moisture")
            guidance.append("Avoid water stress")
        else:
            guidance.append("Maintain regular watering schedule")
            guidance.append("Ensure good drainage")
        
        # Weather-based guidance
        if weather_data and "raw" in weather_data:
            weather = weather_data["raw"]
            if weather.get("rainfall", 0) > 5:
                guidance.append(f"⛈️ Recent rainfall detected - skip watering for 2-3 days")
            if weather.get("humidity", 0) > 80:
                guidance.append("High humidity - reduce watering frequency")
        
        return guidance
    
    def _estimate_treatment_cost(self, disease: str, crop: str, risk_level: str) -> Dict:
        """Estimate treatment costs"""
        # Simplified cost estimation
        base_cost = 500  # INR
        
        if risk_level == "CRITICAL":
            multiplier = 2.0
        elif risk_level == "HIGH":
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        estimated_cost = base_cost * multiplier
        
        return {
            "estimated_cost_inr": f"₹{estimated_cost:.0f} - ₹{estimated_cost * 1.5:.0f}",
            "estimated_cost_usd": f"${estimated_cost / 83:.1f} - ${estimated_cost * 1.5 / 83:.1f}",
            "breakdown": {
                "fungicide_pesticide": f"₹{estimated_cost * 0.6:.0f}",
                "fertilizers": f"₹{estimated_cost * 0.25:.0f}",
                "labor_application": f"₹{estimated_cost * 0.15:.0f}"
            },
            "note": "Costs are estimates and vary by region and product brand"
        }
    
    def _healthy_recommendations(self, crop: str, weather_data: Optional[Dict], soil_type: Optional[str]) -> Dict:
        """Recommendations for healthy plants"""
        return {
            "disease": "Healthy",
            "crop": crop,
            "risk_level": "LOW",
            "immediate_actions": [
                "✅ No immediate action required",
                "Continue regular monitoring"
            ],
            "treatments": [],
            "fertilizer_recommendations": self._get_fertilizer_recommendations(crop, "healthy", soil_type),
            "irrigation_guidance": [
                "Maintain regular watering schedule",
                "Water deeply but infrequently",
                "Ensure good soil drainage"
            ],
            "preventive_measures": [
                "🛡️ Continue preventive care to maintain plant health",
                "Regular inspection for early disease detection",
                "Maintain proper plant spacing",
                "Ensure adequate nutrition",
                "Practice crop rotation",
                "Remove weeds regularly",
                "Mulch to retain moisture and suppress weeds"
            ],
            "monitoring_schedule": {
                "frequency": "Weekly inspection",
                "key_indicators": [
                    "Leaf color and vigor",
                    "Growth rate",
                    "Pest presence",
                    "Soil moisture"
                ]
            },
            "cost_estimate": {
                "estimated_cost_inr": "₹200 - ₹500 per month",
                "estimated_cost_usd": "$2.5 - $6 per month",
                "breakdown": {
                    "fertilizers": "₹150",
                    "pest_prevention": "₹100",
                    "other": "₹50"
                },
                "note": "Routine maintenance costs"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_generic_recommendations(self, disease: str, crop: str) -> Dict:
        """Fallback generic recommendations"""
        return {
            "disease": disease,
            "crop": crop,
            "risk_level": "MEDIUM",
            "immediate_actions": [
                "Consult local agricultural extension office",
                "Document symptoms with photos",
                "Monitor plant progression"
            ],
            "treatments": [
                {
                    "type": "General",
                    "name": "Consult expert for specific treatment",
                    "note": "Treatment depends on accurate disease identification"
                }
            ],
            "preventive_measures": [
                "Maintain plant health",
                "Regular monitoring",
                "Good cultural practices"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instance
_decision_engine = None

def get_decision_engine() -> DecisionEngineService:
    """Get or create decision engine singleton"""
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = DecisionEngineService()
    return _decision_engine
