"""Factory for creating different memory backends."""

from typing import Callable, Dict, Optional

from config.settings import RiskGPTSettings
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

# Mapping of memory backend names to creator callables
_CREATORS: Dict[str, Callable[[RiskGPTSettings], Optional[object]]] = {}


def register_memory_backend(
    name: str, creator: Callable[[RiskGPTSettings], Optional[object]]
) -> None:
    """Register a new memory backend.

    Parameters
    ----------
    name:
        Identifier for the memory backend.
    creator:
        Callable that accepts :class:`RiskGPTSettings` and returns a
        memory instance.
    """

    _CREATORS[name] = creator


def _buffer_memory(_: RiskGPTSettings) -> ConversationBufferMemory:
    """Default in-memory conversation buffer."""

    return ConversationBufferMemory(return_messages=True)


def _redis_memory(settings: RiskGPTSettings) -> ConversationBufferMemory:
    """Redis-based conversation memory."""

    if not settings.REDIS_URL:
        raise ValueError("REDIS_URL must be set for redis memory backend")
    history = RedisChatMessageHistory(url=settings.REDIS_URL, session_id="default")
    return ConversationBufferMemory(chat_memory=history, return_messages=True)


# Register built-in backends
register_memory_backend("none", lambda _s: None)
register_memory_backend("buffer", _buffer_memory)
register_memory_backend("redis", _redis_memory)


def get_memory(settings: RiskGPTSettings = RiskGPTSettings()) -> Optional[object]:
    """Return a memory implementation based on the provided settings."""

    mem_type = settings.MEMORY_TYPE
    creator = _CREATORS.get(mem_type)
    if creator is None:
        available = ", ".join(sorted(_CREATORS)) or "none"
        raise ValueError(
            f"Unsupported memory type '{mem_type}'. Available types: {available}"
        )
    return creator(settings)
