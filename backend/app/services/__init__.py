"""
AI Services Initialization
"""

from typing import Callable, TypeVar

T = TypeVar("T")


def _load_service(loader: Callable[[], T], service_name: str) -> T:
    """Lazily import optional AI services to avoid startup-time hard failures."""
    try:
        return loader()
    except ModuleNotFoundError as exc:
        missing_module = exc.name or "required dependency"
        raise RuntimeError(
            f"{service_name} dependencies are not installed. Missing module: {missing_module}. "
            "Install full backend dependencies with 'pip install -r requirements.txt'."
        ) from exc


def get_vision_service():
    from .vision_model import get_vision_service as _get_vision_service
    return _load_service(_get_vision_service, "Vision service")


def get_weather_service():
    from .weather_service import get_weather_service as _get_weather_service
    return _load_service(_get_weather_service, "Weather service")


def get_fusion_service():
    from .multimodal_fusion import get_fusion_service as _get_fusion_service
    return _load_service(_get_fusion_service, "Multimodal fusion service")


def get_decision_engine():
    from .decision_engine import get_decision_engine as _get_decision_engine
    return _load_service(_get_decision_engine, "Decision engine")


def get_chatbot_service():
    from .rag_chatbot import get_chatbot_service as _get_chatbot_service
    return _load_service(_get_chatbot_service, "Chatbot service")

__all__ = [
    "get_vision_service",
    "get_weather_service",
    "get_fusion_service",
    "get_decision_engine",
    "get_chatbot_service"
]
