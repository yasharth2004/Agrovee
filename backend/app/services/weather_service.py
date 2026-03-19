"""
Weather Service
Fetches real-time weather data.
Primary: OpenWeatherMap API (with API key)
Fallback: Open-Meteo API (free, no key required)
"""

import httpx
import logging
from typing import Dict, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# WMO codes for Open-Meteo fallback
WMO_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snowfall", 73: "moderate snowfall", 75: "heavy snowfall",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}


class WeatherService:
    """
    Real-time weather service.
    Primary: OpenWeatherMap  |  Fallback: Open-Meteo
    """

    def __init__(self):
        self.owm_api_key = settings.WEATHER_API_KEY
        self.owm_base_url = settings.WEATHER_API_URL
        self._geo_cache: Dict[str, tuple] = {}

        # Check if we have a real OWM key
        self._owm_available = (
            self.owm_api_key
            and self.owm_api_key != "your-openweathermap-api-key"
        )
        if self._owm_available:
            logger.info(f"✓ OpenWeatherMap API key configured")
        else:
            logger.warning("OpenWeatherMap key not set — will use Open-Meteo fallback")

    # ==================================================================
    # Public API
    # ==================================================================

    def get_current_weather(self, location: str) -> Dict:
        """Get current weather for a location (city name or 'lat,lon')."""

        # --- Try OpenWeatherMap first ---
        if self._owm_available:
            try:
                return self._fetch_owm(location)
            except Exception as e:
                logger.warning(f"OpenWeatherMap failed, falling back to Open-Meteo: {e}")

        # --- Fallback: Open-Meteo (free, no key) ---
        try:
            return self._fetch_open_meteo(location)
        except Exception as e:
            logger.error(f"Open-Meteo also failed: {e}")
            return self._static_fallback(location)

    def get_weather_features(self, location: str) -> Dict:
        """Normalized weather features for the multimodal fusion model."""
        weather = self.get_current_weather(location)
        features = {
            "temperature_norm": min(max(weather["temperature"] / 50.0, 0), 1),
            "humidity_norm": weather["humidity"] / 100.0,
            "rainfall_norm": min(weather["rainfall"] / 10.0, 1),
            "wind_speed_norm": min(weather["wind_speed"] / 20.0, 1),
        }
        return {"raw": weather, "features": features}

    # ==================================================================
    # OpenWeatherMap
    # ==================================================================

    def _fetch_owm(self, location: str) -> Dict:
        """Fetch weather from OpenWeatherMap."""
        url = f"{self.owm_base_url}/weather"
        params = {
            "q": location,
            "appid": self.owm_api_key,
            "units": "metric",
        }

        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

        weather_info = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "rainfall": data.get("rain", {}).get("1h", 0.0),
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "location": data["name"],
            "timestamp": datetime.utcnow().isoformat(),
            "source": "OpenWeatherMap",
        }

        logger.info(
            f"✓ OWM weather for {data['name']}: "
            f"{weather_info['temperature']}°C, {weather_info['description']}"
        )
        return weather_info

    # ==================================================================
    # Open-Meteo (fallback — free, no API key)
    # ==================================================================

    GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

    def _fetch_open_meteo(self, location: str) -> Dict:
        """Fetch weather from Open-Meteo (free fallback)."""
        lat, lon, resolved_name = self._geocode(location)

        resp = httpx.get(
            self.OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "hourly": "relative_humidity_2m,rain,surface_pressure",
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

        cw = data["current_weather"]
        hourly = data.get("hourly", {})
        hour_idx = self._current_hour_index(hourly.get("time", []))

        humidity = self._safe_index(hourly.get("relative_humidity_2m"), hour_idx, 50.0)
        rainfall = self._safe_index(hourly.get("rain"), hour_idx, 0.0)
        pressure = self._safe_index(hourly.get("surface_pressure"), hour_idx, 1013.0)
        wmo = cw.get("weathercode", 0)

        weather_info = {
            "temperature": cw["temperature"],
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": cw["windspeed"] / 3.6,  # km/h → m/s
            "rainfall": rainfall,
            "description": WMO_CODES.get(wmo, "unknown"),
            "icon": "02d",
            "location": resolved_name,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "Open-Meteo",
        }

        logger.info(
            f"✓ Open-Meteo weather for {resolved_name}: "
            f"{weather_info['temperature']}°C, {weather_info['description']}"
        )
        return weather_info

    # ==================================================================
    # Helpers
    # ==================================================================

    def _geocode(self, location: str) -> tuple:
        """Resolve city name → (lat, lon, name) via Open-Meteo geocoding."""
        cache_key = location.strip().lower()
        if cache_key in self._geo_cache:
            return self._geo_cache[cache_key]

        if "," in location:
            parts = location.split(",")
            try:
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
                result = (lat, lon, f"{lat},{lon}")
                self._geo_cache[cache_key] = result
                return result
            except ValueError:
                pass

        resp = httpx.get(
            self.GEOCODE_URL,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=10.0,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            raise ValueError(f"Location not found: {location}")

        r = results[0]
        lat, lon = r["latitude"], r["longitude"]
        name = r.get("name", location)
        country = r.get("country", "")
        resolved = f"{name}, {country}" if country else name

        self._geo_cache[cache_key] = (lat, lon, resolved)
        return (lat, lon, resolved)

    @staticmethod
    def _current_hour_index(time_list: list) -> int:
        if not time_list:
            return 0
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:00")
        for i, t in enumerate(time_list):
            if t >= now_str:
                return i
        return len(time_list) - 1

    @staticmethod
    def _safe_index(lst, idx, default):
        if lst and 0 <= idx < len(lst):
            return lst[idx]
        return default

    @staticmethod
    def _static_fallback(location: str) -> Dict:
        """Last-resort static fallback."""
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
            "source": "static-fallback",
            "note": "Both weather APIs unavailable",
        }


# Global instance
_weather_service = None


def get_weather_service() -> WeatherService:
    """Get or create weather service singleton"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
