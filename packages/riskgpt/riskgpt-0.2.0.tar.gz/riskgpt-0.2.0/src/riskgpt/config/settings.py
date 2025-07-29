from typing import Literal, Optional

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RiskGPTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", env_ignore_empty=True, extra="ignore"
    )

    MEMORY_TYPE: Literal["none", "buffer", "redis"] = Field(default="buffer")
    REDIS_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[SecretStr] = None
    TEMPERATURE: float = Field(default=0.7, ge=0.0, le=1.0)
    MAX_TOKENS: Optional[int] = None
    OPENAI_MODEL_NAME: str = Field(default="openai:gpt-4.1-nano")
    DEFAULT_PROMPT_VERSION: str = Field(default="v1")

    # Search provider settings
    SEARCH_PROVIDER: Literal["duckduckgo", "google", "wikipedia", "tavily"] = Field(
        default="duckduckgo"
    )
    MAX_SEARCH_RESULTS: int = Field(default=3, ge=1, le=100)
    INCLUDE_WIKIPEDIA: bool = Field(default=False)
    GOOGLE_CSE_ID: Optional[str] = None
    GOOGLE_API_KEY: Optional[SecretStr] = None
    TAVILY_API_KEY: Optional[SecretStr] = None

    # Document service settings
    DOCUMENT_SERVICE_URL: Optional[str] = None

    @field_validator("MEMORY_TYPE")
    @classmethod
    def validate_memory_type(cls, v: str) -> str:
        from helpers.memory_factory import _CREATORS

        allowed = {"none", "buffer", "redis"}.union(_CREATORS.keys())
        if v not in allowed:
            raise ValueError("Input should be 'none', 'buffer' or 'redis'")
        return v
