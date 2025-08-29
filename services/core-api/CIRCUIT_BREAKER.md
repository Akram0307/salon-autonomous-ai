# Circuit Breaker Implementation

This document describes the circuit breaker implementation for the core-api service, following Google Cloud's recommended practices.

## Overview

The circuit breaker pattern is used to improve system resilience by preventing continuous failures in a system. It acts as a safeguard by monitoring requests and stopping repeated failures from affecting performance.

## Implementation Details

The circuit breaker is implemented using the `fastapi-cb` library, which provides a decorator-based approach to add circuit breaker functionality to FastAPI applications.

### Configuration

The circuit breaker is configured with the following parameters:

- **Failure Threshold**: 5 failures before opening the circuit
- **Timeout**: 60 seconds before trying again
- **Expected Exception**: Catches all exceptions based on the Exception class

### Usage

To use the circuit breaker in your FastAPI endpoints, you can decorate your functions with the `@with_circuit_breaker` decorator:

```python
from .circuit_breaker.circuit_breaker import with_circuit_breaker

@app.get("/external-service-call")
@with_circuit_breaker
async def call_external_service():
    """Example endpoint that demonstrates circuit breaker usage"""
    # Your code here
```

### Fallback Handling

When the circuit breaker is open, a `CircuitBreakerOpen` exception is raised. This is handled globally in the FastAPI application with an exception handler that returns a 503 Service Unavailable response.

## Google Cloud Best Practices

This implementation follows Google Cloud's recommended practices for implementing circuit breakers:

1. **Failure Threshold**: Set an appropriate threshold to prevent cascading failures
2. **Timeout Period**: Allow sufficient time for the service to recover before retrying
3. **Fallback Mechanisms**: Provide graceful degradation when the circuit is open
4. **Monitoring**: Log circuit breaker events for observability

## Integration with Existing Services

The circuit breaker can be easily integrated into existing FastAPI applications by:

1. Adding the `fastapi-cb` dependency to your requirements
2. Importing the circuit breaker decorator
3. Decorating your external service calls with the circuit breaker
4. Handling the `CircuitBreakerOpen` exception appropriately

## Example

See the `/external-service-call` and `/external-service-call-with-fallback` endpoints in `main.py` for example implementations.
