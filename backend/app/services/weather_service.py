"""
Weather Service
Fetches weather data from OpenWeatherMap API
"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for fetching weather data
    Uses OpenWeatherMap API
    """
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_URL
    
    def get_current_weather(self, location: str) -> Dict:
        """
        Get current weather for a location
        
        Args:
            location: City name or coordinates (lat,lon)
            
        Returns:
            Weather data dictionary
        """
        try:
            # Build API URL
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"  # Celsius
            }
            
            # Make request
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "location": data["name"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add rain data if available
            if "rain" in data:
                weather_info["rainfall"] = data["rain"].get("1h", 0)
            else:
                weather_info["rainfall"] = 0
            
            logger.info(f"Weather fetched for {location}: {weather_info['temperature']}°C")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            # Return dummy data for development
            return self._get_dummy_weather(location)
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return self._get_dummy_weather(location)
    
    def _get_dummy_weather(self, location: str) -> Dict:
        """Return dummy weather data for development"""
        return {
            "temperature": 25.0,
            "humidity": 65.0,
            "pressure": 1013.0,
            "wind_speed": 5.5,
            "rainfall": 0.0,
            "description": "partly cloudy",
            "icon": "02d",
            "location": location or "Unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Demo data - API key not configured"
        }
    
    def get_weather_features(self, location: str) -> Dict:
        """
        Get weather features for multimodal fusion
        
        Returns normalized features suitable for ML model input
        """
        weather = self.get_current_weather(location)
        
        # Normalize features to 0-1 range (approximate normalization)
        features = {
            "temperature_norm": min(max(weather["temperature"] / 50.0, 0), 1),  # 0-50°C range
            "humidity_norm": weather["humidity"] / 100.0,  # 0-100% range
            "rainfall_norm": min(weather["rainfall"] / 10.0, 1),  # 0-10mm range
            "wind_speed_norm": min(weather["wind_speed"] / 20.0, 1),  # 0-20 m/s range
        }
        
        return {
            "raw": weather,
            "features": features
        }


# Global instance
_weather_service = None

def get_weather_service() -> WeatherService:
    """Get or create weather service singleton"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
