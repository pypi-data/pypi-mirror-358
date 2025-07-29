"""Circuit breaker implementation for external API calls.

This module provides a circuit breaker pattern implementation for external API calls
to handle service outages gracefully. It uses the pybreaker library if available,
otherwise it provides a fallback implementation that doesn't break the circuit.

The circuit breaker pattern prevents sending requests to services that are likely
to fail, reducing latency and conserving resources. It also allows the application
to degrade gracefully when external services are unavailable.
"""

import functools
from typing import Any, Callable, TypeVar

import pybreaker
from logger import logger

# Type variable for function return type
T = TypeVar("T")

# Create circuit breakers for different services
openai_breaker = pybreaker.CircuitBreaker(
    fail_max=5,  # Number of failures before opening the circuit
    reset_timeout=60,  # Seconds before attempting to close the circuit
    exclude=[ValueError],  # Exceptions that shouldn't count as failures
)

duckduckgo_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # Number of failures before opening the circuit
    reset_timeout=30,  # Seconds before attempting to close the circuit
)

google_search_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # Number of failures before opening the circuit
    reset_timeout=30,  # Seconds before attempting to close the circuit
)

wikipedia_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # Number of failures before opening the circuit
    reset_timeout=30,  # Seconds before attempting to close the circuit
)

tavily_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # Number of failures before opening the circuit
    reset_timeout=30,  # Seconds before attempting to close the circuit
)

document_service_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
)


class CircuitStateListener(pybreaker.CircuitBreakerListener):
    """Listener that logs circuit state changes."""

    def state_change(self, cb, old_state, new_state):
        """Called when the circuit breaker state changes."""
        logger.warning(
            "Circuit breaker state change: %s -> %s", old_state.name, new_state.name
        )


# Add the listener to the circuit breakers
openai_breaker.add_listener(CircuitStateListener())
duckduckgo_breaker.add_listener(CircuitStateListener())
google_search_breaker.add_listener(CircuitStateListener())
wikipedia_breaker.add_listener(CircuitStateListener())
tavily_breaker.add_listener(CircuitStateListener())
document_service_breaker.add_listener(CircuitStateListener())


def with_fallback(
    fallback_func: Callable[..., T],
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that provides a fallback function when the circuit is open.

    Args:
        fallback_func: The function to call when the circuit is open

    Returns:
        A decorator that wraps a function with a fallback
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, pybreaker.CircuitBreakerError):
                    logger.warning(
                        "Circuit is open for %s, using fallback", func.__name__
                    )
                    return fallback_func(*args, **kwargs)
                # Also use fallback for any other exception
                logger.warning(
                    "Exception in %s, using fallback: %s", func.__name__, str(e)
                )
                return fallback_func(*args, **kwargs)

        return wrapper

    return decorator
