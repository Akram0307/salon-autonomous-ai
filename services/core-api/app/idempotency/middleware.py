from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging
from .storage import idempotency_store
from .models import IdempotencyKey
from typing import Callable, Awaitable
import json

logger = logging.getLogger(__name__)


class IdempotencyMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Check if this is a request that should be idempotent
        if request.method in ["POST", "PUT", "PATCH"]:
            idempotency_key = request.headers.get("Idempotency-Key")
            
            if idempotency_key:
                # Check if we have already processed this key
                existing_key = await idempotency_store.get(idempotency_key)
                
                if existing_key:
                    # Return the stored response
                    logger.info(f"Returning cached response for idempotency key: {idempotency_key}")
                    response = Response(
                        content=json.dumps(existing_key.response_body),
                        status_code=existing_key.response_code,
                        headers={"Content-Type": "application/json"}
                    )
                    await response(scope, receive, send)
                    return
        
        # Continue with the request processing
        await self.app(scope, receive, send)


def idempotent_request(ttl_seconds: int = 86400):
    """
    Decorator to make a FastAPI endpoint idempotent
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Get request from args or kwargs
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request and request.method in ["POST", "PUT", "PATCH"]:
                idempotency_key = request.headers.get("Idempotency-Key")
                
                if idempotency_key:
                    # Check if we have already processed this key
                    existing_key = await idempotency_store.get(idempotency_key)
                    
                    if existing_key:
                        # Return the stored response
                        logger.info(f"Returning cached response for idempotency key: {idempotency_key}")
                        return JSONResponse(
                            content=existing_key.response_body,
                            status_code=existing_key.response_code
                        )
            
            # Execute the original function
            response = await func(*args, **kwargs)
            
            # Store the response if idempotency key was provided
            if request and request.method in ["POST", "PUT", "PATCH"]:
                idempotency_key = request.headers.get("Idempotency-Key")
                
                if idempotency_key and response:
                    # Extract response data
                    response_code = response.status_code
                    response_body = getattr(response, 'body', None)
                    
                    # If it's a JSONResponse, we can get the content directly
                    if hasattr(response, 'body'):
                        try:
                            response_body = json.loads(response.body.decode())
                        except:
                            response_body = response.body.decode()
                    elif hasattr(response, 'content'):
                        response_body = response.content
                    
                    # Store the idempotency key with response data
                    await idempotency_store.set(
                        idempotency_key, 
                        response_code, 
                        response_body, 
                        ttl_seconds
                    )
                    logger.info(f"Stored response for idempotency key: {idempotency_key}")
            
            return response
        return wrapper
    return decorator
