import asyncio
import time
from typing import Optional, Dict, Any
from .models import IdempotencyKey
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class InMemoryIdempotencyStore:
    def __init__(self, default_ttl_seconds: int = 86400):  # 24 hours default
        self._store: Dict[str, IdempotencyKey] = {}
        self._lock = asyncio.Lock()
        self.default_ttl_seconds = default_ttl_seconds
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_keys())
    
    async def _cleanup_expired_keys(self):
        """Periodically clean up expired idempotency keys"""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                now = datetime.utcnow()
                expired_keys = [
                    key for key, idempotency_key in self._store.items()
                    if idempotency_key.expires_at < now
                ]
                for key in expired_keys:
                    del self._store[key]
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired idempotency keys")
            except Exception as e:
                logger.error(f"Error during idempotency key cleanup: {e}")
    
    async def get(self, key: str) -> Optional[IdempotencyKey]:
        """Retrieve an idempotency key if it exists and hasn't expired"""
        async with self._lock:
            if key in self._store:
                idempotency_key = self._store[key]
                # Check if key has expired
                if idempotency_key.expires_at < datetime.utcnow():
                    del self._store[key]
                    return None
                return idempotency_key
            return None
    
    async def set(self, key: str, response_code: int, response_body: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store an idempotency key with its response"""
        async with self._lock:
            try:
                ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
                now = datetime.utcnow()
                expires_at = now + timedelta(seconds=ttl)
                
                idempotency_key = IdempotencyKey(
                    key=key,
                    response_code=response_code,
                    response_body=response_body,
                    created_at=now,
                    expires_at=expires_at
                )
                
                self._store[key] = idempotency_key
                return True
            except Exception as e:
                logger.error(f"Error storing idempotency key {key}: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """Delete an idempotency key"""
        async with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False
    
    def __del__(self):
        """Clean up the cleanup task when the store is deleted"""
        if hasattr(self, '_cleanup_task'):
            self._cleanup_task.cancel()

# Global instance for the application
idempotency_store = InMemoryIdempotencyStore()
