"""Configuration helper for memory backends."""

from typing import Literal, Optional

from config.settings import RiskGPTSettings
from helpers.memory_factory import get_memory as factory_get_memory
from pydantic_settings import BaseSettings


class MemorySettings(BaseSettings):
    """Settings for memory creation."""

    type: Literal["none", "buffer", "redis"] = "buffer"
    redis_url: Optional[str] = None


def get_memory(settings: MemorySettings = MemorySettings()):
    return factory_get_memory(
        RiskGPTSettings(MEMORY_TYPE=settings.type, REDIS_URL=settings.redis_url)
    )
