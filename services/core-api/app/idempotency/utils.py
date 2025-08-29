from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from .storage import idempotency_store
import json

logger = logging.getLogger(__name__)


def check_idempotency_key(request: Request):
    """Check if an idempotency key exists in the request headers"""
    return request.headers.get("Idempotency-Key")


async def get_cached_response(idempotency_key: str):
    """Get cached response for an idempotency key if it exists"""
    existing_key = await idempotency_store.get(idempotency_key)
    if existing_key:
        logger.info(f"Returning cached response for idempotency key: {idempotency_key}")
        return JSONResponse(
            content=existing_key.response_body,
            status_code=existing_key.response_code
        )
    return None


async def store_response(idempotency_key: str, response: JSONResponse, ttl_seconds: int = 86400):
    """Store response for an idempotency key"""
    try:
        # Extract response data
        response_code = response.status_code
        response_body = response.body.decode() if hasattr(response, 'body') else ""
        
        # Try to parse JSON response body
        try:
            parsed_body = json.loads(response_body)
        except:
            parsed_body = response_body
        
        # Store the idempotency key with response data
        success = await idempotency_store.set(
            idempotency_key, 
            response_code, 
            parsed_body, 
            ttl_seconds
        )
        
        if success:
            logger.info(f"Stored response for idempotency key: {idempotency_key}")
        else:
            logger.error(f"Failed to store response for idempotency key: {idempotency_key}")
            
    except Exception as e:
        logger.error(f"Error storing response for idempotency key {idempotency_key}: {e}")
