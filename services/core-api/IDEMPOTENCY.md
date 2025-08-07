# Idempotency Key Implementation

This document describes the idempotency key implementation for the core-api service.

## Overview

The idempotency key implementation allows POST, PUT, and PATCH requests to be safely retried without causing duplicate operations. When a client includes an `Idempotency-Key` header in their request, the system will store the response for that key and return the same response for subsequent requests with the same key.

## Implementation Details

### Components

1. **Models** (`app/idempotency/models.py`): Defines the `IdempotencyKey` data model.
2. **Storage** (`app/idempotency/storage.py`): Implements an in-memory store for idempotency keys with thread-safe operations and automatic cleanup of expired keys.
3. **Utilities** (`app/idempotency/utils.py`): Provides utility functions for checking idempotency keys and managing cached responses.
4. **Decorator** (`app/idempotency/decorator.py`): Provides the `@idempotent` decorator that can be applied to FastAPI endpoints.

### Usage

To make an endpoint idempotent, simply add the `@idempotent` decorator:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .idempotency.decorator import idempotent

app = FastAPI()

@app.post("/bookings")
@idempotent(ttl_seconds=3600)  # 1 hour TTL
async def create_booking(booking: BookingRequest, request: Request):
    # Implementation here
    pass
```

### Thread Safety

The idempotency store uses `asyncio.Lock()` to ensure thread-safe operations when accessing the in-memory store.

### Key Expiration

Idempotency keys automatically expire after a configurable TTL (default 24 hours). A background task runs every 5 minutes to clean up expired keys.

## Client Usage

Clients should include an `Idempotency-Key` header in their requests:

```http
POST /bookings HTTP/1.1
Host: api.example.com
Idempotency-Key: 7e0b5145-1d2c-4f0e-9f2a-8c3d9a1b2c3d
Content-Type: application/json

{
  "service_id": "service_123",
  "customer_name": "John Doe",
  "date": "2025-08-07",
  "time": "10:00"
}
```

## Testing

A test script is available at `test_idempotency.py` to demonstrate the functionality.

## Extending to Persistent Storage

The current implementation uses an in-memory store. To extend this to use a persistent store like Firestore (as in the booking-api-fastapi service), you would need to:

1. Modify `app/idempotency/storage.py` to use Firestore instead of the in-memory dictionary
2. Implement Firestore transactions for atomic read/write operations
3. Add appropriate error handling for network and database issues

The structure is already designed to allow this extension by abstracting the storage mechanism.
