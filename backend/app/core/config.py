"""
Application Configuration
Centralized settings management using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    All settings can be overridden via .env file
    """
    
    # Application
    PROJECT_NAME: str = "Agrovee API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # Backend
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./agrovee.db"  # Use SQLite for local testing
    DATABASE_ECHO: bool = False  # Set to True to log SQL queries
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-min32chars!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Password Hashing
    PWD_CONTEXT_SCHEMES: List[str] = ["bcrypt"]
    PWD_DEPRECATED_SCHEMES: str = "auto"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    
    # AI Models
    MODEL_PATH: str = "../p1/models/best_model.pth"
    MODEL_METADATA_PATH: str = "../p1/models/metadata.json"
    DEVICE: str = "cuda"  # or "cpu"
    
    # Weather API (OpenWeatherMap)
    WEATHER_API_KEY: str = "fa64060dde08540c194cff5e6c86fd5f"
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # HuggingFace (for RAG chatbot)
    HUGGINGFACE_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # FAISS Vector DB
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    
    # Redis Cache (optional)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Use this function to access settings throughout the application
    """
    return Settings()


# Global settings instance
settings = get_settings()
