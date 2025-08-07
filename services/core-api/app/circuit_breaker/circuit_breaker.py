"""
Circuit Breaker Implementation for Core-API Service

This module implements the circuit breaker pattern following Google Cloud's recommended practices.
"""

import logging
from typing import Any, Callable, Optional
from fastapi import HTTPException, status
from fastapi_cb import circuit_breaker

# Set up logging
logger = logging.getLogger(__name__)

# Circuit breaker configuration
FAILURE_THRESHOLD = 5  # Number of failures before opening the circuit
TIMEOUT = 60  # Timeout in seconds before trying again
EXPECTED_EXCEPTION = Exception  # Exception type to catch


class CoreAPICircuitBreaker:
    """Circuit Breaker for Core-API Service"""

    def __init__(self, 
                 failure_threshold: int = FAILURE_THRESHOLD,
                 timeout: int = TIMEOUT,
                 expected_exception: Exception = EXPECTED_EXCEPTION):
        """
        Initialize the circuit breaker with configuration parameters.

        Args:
            failure_threshold: Number of failures before opening the circuit
            timeout: Timeout in seconds before trying again
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        # Create the circuit breaker decorator
        self.cb_decorator = circuit_breaker(
            failure_threshold=self.failure_threshold,
            timeout=self.timeout,
            expected_exception=self.expected_exception
        )

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to apply circuit breaker to a function.

        Args:
            func: Function to decorate

        Returns:
            Decorated function with circuit breaker
        """
        return self.cb_decorator(func)


def fallback_handler(exception: Exception) -> Any:
    """
    Fallback handler for when the circuit breaker is open.

    Args:
        exception: The exception that caused the circuit breaker to open

    Returns:
        Fallback response
    """
    logger.warning(f"Circuit breaker is open. Exception: {exception}")

    # Return a fallback response
    return {
        "error": "Service temporarily unavailable",
        "message": "The service is currently unavailable. Please try again later.",
        "status": "circuit_open"
    }


def create_circuit_breaker(failure_threshold: int = FAILURE_THRESHOLD,
                          timeout: int = TIMEOUT,
                          expected_exception: Exception = EXPECTED_EXCEPTION) -> CoreAPICircuitBreaker:
    """
    Factory function to create a circuit breaker instance.

    Args:
        failure_threshold: Number of failures before opening the circuit
        timeout: Timeout in seconds before trying again
        expected_exception: Exception type to catch

    Returns:
        CoreAPICircuitBreaker instance
    """
    return CoreAPICircuitBreaker(
        failure_threshold=failure_threshold,
        timeout=timeout,
        expected_exception=expected_exception
    )


# Default circuit breaker instance
DEFAULT_CIRCUIT_BREAKER = create_circuit_breaker()

# Decorator for easy use
with_circuit_breaker = DEFAULT_CIRCUIT_BREAKER
