from functools import wraps
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from .utils import check_idempotency_key, get_cached_response, store_response

logger = logging.getLogger(__name__)


def idempotent(ttl_seconds: int = 86400):
    """
    Decorator to make a FastAPI endpoint idempotent
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            # Check if this is a request that should be idempotent
            if request and request.method in ["POST", "PUT", "PATCH"]:
                idempotency_key = check_idempotency_key(request)
                
                if idempotency_key:
                    # Check if we have already processed this key
                    cached_response = await get_cached_response(idempotency_key)
                    
                    if cached_response:
                        return cached_response
            
            # Execute the original function
            response = await func(*args, **kwargs)
            
            # Store the response if idempotency key was provided
            if request and request.method in ["POST", "PUT", "PATCH"]:
                idempotency_key = check_idempotency_key(request)
                
                if idempotency_key and isinstance(response, JSONResponse):
                    await store_response(idempotency_key, response, ttl_seconds)
            
            return response
        return wrapper
    return decorator
