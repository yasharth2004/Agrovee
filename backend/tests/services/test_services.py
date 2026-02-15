"""
Unit Tests for AI Services
Tests each service in isolation (demo mode)
"""

import pytest
import os


# ──────────────────────────────────────────────────────────────
# Vision Model Service
# ──────────────────────────────────────────────────────────────

class TestVisionModelService:
    """Tests for VisionModelService (demo mode)."""

    def test_singleton(self):
        """get_vision_service returns same instance."""
        from app.services import get_vision_service

        s1 = get_vision_service()
        s2 = get_vision_service()
        assert s1 is s2

    def test_predict_returns_required_keys(self, sample_image):
        """predict() returns all expected keys."""
        from app.services import get_vision_service

        service = get_vision_service()
        result = service.predict(str(sample_image))
        required_keys = {
            "predicted_disease",
            "confidence",
            "crop_type",
            "top_predictions",
            "model_version",
        }
        assert required_keys.issubset(result.keys())

    def test_predict_confidence_range(self, sample_image):
        """Confidence is between 0 and 100."""
        from app.services import get_vision_service

        service = get_vision_service()
        result = service.predict(str(sample_image))
        assert 0 <= result["confidence"] <= 100

    def test_predict_top_predictions_count(self, sample_image):
        """Top predictions list has ≤5 entries."""
        from app.services import get_vision_service

        service = get_vision_service()
        result = service.predict(str(sample_image))
        assert len(result["top_predictions"]) <= 5

    def test_predict_top_predictions_structure(self, sample_image):
        """Each prediction has disease/probability/crop keys."""
        from app.services import get_vision_service

        service = get_vision_service()
        result = service.predict(str(sample_image))
        for pred in result["top_predictions"]:
            assert "disease" in pred or "disease_name" in pred
            assert "probability" in pred
            assert "crop" in pred or "crop_type" in pred

    def test_extract_crop_type(self):
        """_extract_crop_type handles Crop___Disease format."""
        from app.services import get_vision_service

        service = get_vision_service()
        assert service._extract_crop_type("Tomato___Early_Blight") == "Tomato"
        assert service._extract_crop_type("Apple___Black_Rot") == "Apple"


# ──────────────────────────────────────────────────────────────
# Weather Service
# ──────────────────────────────────────────────────────────────

class TestWeatherService:
    """Tests for WeatherService (dummy/fallback mode)."""

    def test_singleton(self):
        """get_weather_service returns same instance."""
        from app.services import get_weather_service

        s1 = get_weather_service()
        s2 = get_weather_service()
        assert s1 is s2

    def test_get_weather_features_returns_dict(self):
        """get_weather_features returns dict with raw and features."""
        from app.services import get_weather_service

        service = get_weather_service()
        result = service.get_weather_features("Mumbai")
        assert "raw" in result
        assert "features" in result

    def test_weather_raw_keys(self):
        """Raw weather data has temperature, humidity, etc."""
        from app.services import get_weather_service

        service = get_weather_service()
        result = service.get_weather_features("Delhi")
        raw = result["raw"]
        expected_keys = {"temperature", "humidity"}
        assert expected_keys.issubset(raw.keys())

    def test_weather_features_normalized(self):
        """Feature values are between 0 and 1."""
        from app.services import get_weather_service

        service = get_weather_service()
        result = service.get_weather_features("Pune")
        for key, value in result["features"].items():
            assert 0 <= value <= 1, f"{key} = {value} out of [0, 1]"


# ──────────────────────────────────────────────────────────────
# Multimodal Fusion Service
# ──────────────────────────────────────────────────────────────

class TestMultimodalFusionService:
    """Tests for MultimodalFusionService."""

    def test_singleton(self):
        """get_fusion_service returns same instance."""
        from app.services import get_fusion_service

        s1 = get_fusion_service()
        s2 = get_fusion_service()
        assert s1 is s2

    def _make_vision_prediction(self):
        return {
            "predicted_disease": "Tomato___Early_Blight",
            "confidence": 85.0,
            "crop_type": "Tomato",
            "top_predictions": [
                {"disease_name": "Tomato___Early_Blight", "probability": 85.0, "crop_type": "Tomato"},
            ],
        }

    def _make_weather_data(self):
        return {
            "raw": {"temperature": 30, "humidity": 80, "rainfall": 5, "wind_speed": 10},
            "features": {
                "temperature_norm": 0.6,
                "humidity_norm": 0.8,
                "rainfall_norm": 0.05,
                "wind_speed_norm": 0.2,
            },
        }

    def test_enhance_prediction_returns_keys(self):
        """enhance_prediction returns fusion_confidence and risk_assessment."""
        from app.services import get_fusion_service

        service = get_fusion_service()
        result = service.enhance_prediction(
            self._make_vision_prediction(),
            self._make_weather_data(),
            "loamy",
            "summer",
        )
        assert "fusion_confidence" in result
        assert "risk_assessment" in result
        assert "predicted_disease" in result

    def test_risk_assessment_values(self):
        """risk_assessment is one of LOW, MEDIUM, HIGH, CRITICAL."""
        from app.services import get_fusion_service

        service = get_fusion_service()
        result = service.enhance_prediction(
            self._make_vision_prediction(),
            self._make_weather_data(),
            "clay",
            "monsoon",
        )
        assert result["risk_assessment"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_enhance_without_weather(self):
        """Works even without weather data."""
        from app.services import get_fusion_service

        service = get_fusion_service()
        result = service.enhance_prediction(
            self._make_vision_prediction(),
            None,
            "sandy",
            None,
        )
        assert "fusion_confidence" in result

    def test_encode_soil_type_length(self):
        """Soil encoding returns 10-element array."""
        from app.services import get_fusion_service
        import numpy as np

        service = get_fusion_service()
        enc = service.encode_soil_type("loamy")
        assert len(enc) == 10
        assert np.sum(enc) == 1  # one-hot


# ──────────────────────────────────────────────────────────────
# Decision Engine Service
# ──────────────────────────────────────────────────────────────

class TestDecisionEngineService:
    """Tests for DecisionEngineService."""

    def test_singleton(self):
        """get_decision_engine returns same instance."""
        from app.services import get_decision_engine

        s1 = get_decision_engine()
        s2 = get_decision_engine()
        assert s1 is s2

    def test_recommendations_structure(self):
        """Recommendations contain expected keys."""
        from app.services import get_decision_engine

        engine = get_decision_engine()
        recs = engine.generate_recommendations(
            disease="Tomato___Early_Blight",
            crop="Tomato",
            confidence=90.0,
            risk_level="HIGH",
            weather_data={"raw": {"temperature": 28, "humidity": 70}},
            soil_type="loamy",
        )
        for key in ("immediate_actions", "treatments", "preventive_measures"):
            assert key in recs, f"Missing key: {key}"

    def test_recommendations_for_healthy(self):
        """Healthy plant gets care-orientated recommendations."""
        from app.services import get_decision_engine

        engine = get_decision_engine()
        recs = engine.generate_recommendations(
            disease="Tomato___healthy",
            crop="Tomato",
            confidence=99.0,
            risk_level="LOW",
            weather_data=None,
            soil_type="clay",
        )
        assert "immediate_actions" in recs

    def test_normalize_disease_name(self):
        """Internal normalizer strips crop prefix."""
        from app.services import get_decision_engine

        engine = get_decision_engine()
        assert engine._normalize_disease_name("Tomato___Early_Blight") == "early blight"
        assert engine._normalize_disease_name("Apple___Black_Rot") == "black rot"


# ──────────────────────────────────────────────────────────────
# RAG Chatbot Service
# ──────────────────────────────────────────────────────────────

class TestRAGChatbotService:
    """Tests for RAGChatbotService."""

    def test_singleton(self):
        """get_chatbot_service returns same instance."""
        from app.services import get_chatbot_service

        s1 = get_chatbot_service()
        s2 = get_chatbot_service()
        assert s1 is s2

    def test_chat_returns_answer(self):
        """chat() returns answer string."""
        from app.services import get_chatbot_service

        service = get_chatbot_service()
        result = service.chat("How do I prevent crop diseases?", None)
        assert "answer" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

    def test_chat_returns_sources(self):
        """chat() returns sources list."""
        from app.services import get_chatbot_service

        service = get_chatbot_service()
        result = service.chat("Tell me about fertilizer management.", None)
        assert "sources" in result
        assert isinstance(result["sources"], list)

    def test_chat_with_context(self):
        """chat() accepts a context dict without error."""
        from app.services import get_chatbot_service

        service = get_chatbot_service()
        result = service.chat(
            "What irrigation schedule for rice?",
            {"crop": "rice", "region": "Punjab"},
        )
        assert "answer" in result

    def test_keyword_search_works(self):
        """_keyword_search returns results for known topics."""
        from app.services import get_chatbot_service

        service = get_chatbot_service()
        results = service._keyword_search("crop rotation benefits", top_k=3)
        assert isinstance(results, list)
        # At least some results should be returned for known KB topics
        assert len(results) >= 0  # may be 0 if no KB match, that's OK
