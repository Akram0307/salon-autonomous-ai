import json
import base64
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
import uuid
import logging
from .idempotency.decorator import idempotent
from .circuit_breaker.circuit_breaker import with_circuit_breaker, fallback_handler
from fastapi.responses import JSONResponse

# Import the events router
from .events.example_usage import router as events_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Import circuit breaker for external service calls
app = FastAPI()

# Include the events router
app.include_router(events_router, prefix="/events", tags=["events"])

# Example data model
class BookingRequest(BaseModel):
    service_id: str
    customer_name: str
    date: str
    time: str
    notes: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    service_id: str
    customer_name: str
    date: str
    time: str
    status: str
    notes: Optional[str] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/health")
def health_check():
# Global variable to store the last received booking event
last_received_booking_event = None

@app.post("/pubsub/booking-events")
async def pubsub_booking_events(request: Request):
    """Receives push messages from Pub/Sub subscription."""
    try:
        envelope = await request.json()
        message = envelope['message']

        # Decode the Pub/Sub message data
        data = base64.b64decode(message['data']).decode('utf-8')
        event = json.loads(data)

        # Log the event details
        logger.info(f"Received Pub/Sub message: {event}")

        # Store the last received event
        global last_received_booking_event
        last_received_booking_event = event

        # Acknowledge the message
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.get("/last-booking-event")
def get_last_booking_event():
    """Returns the last received booking event."""
    return {"last_event": last_received_booking_event}

    return {"status": "healthy"}

# Example POST endpoint with idempotency support
@app.post("/bookings", response_model=BookingResponse)
@idempotent(ttl_seconds=3600)  # 1 hour TTL
async def create_booking(booking: BookingRequest, request: Request):
    """Create a booking with idempotency support"""
    logger.info(f"Processing booking request for {booking.customer_name}")
    
    # Simulate some processing time
    import time
    time.sleep(1)
    
    # Create a booking ID (in a real app, this would involve database operations)
    booking_id = str(uuid.uuid4())
    
    # Create response
    response_data = BookingResponse(
        booking_id=booking_id,
        service_id=booking.service_id,
        customer_name=booking.customer_name,
        date=booking.date,
        time=booking.time,
        status="confirmed",
        notes=booking.notes
    )
    
    logger.info(f"Booking created with ID: {booking_id}")
    
    return JSONResponse(content=response_data.dict(), status_code=201)


# Example endpoint with circuit breaker
@app.get("/external-service-call")
@with_circuit_breaker
async def call_external_service():
    """Example endpoint that demonstrates circuit breaker usage"""
    logger.info("Calling external service with circuit breaker")

    # Simulate an external service call that might fail
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("External service is unavailable")

    return {"message": "External service call successful"}

# Example endpoint with circuit breaker and fallback
@app.get("/external-service-call-with-fallback")
@with_circuit_breaker
async def call_external_service_with_fallback():
    """Example endpoint that demonstrates circuit breaker with fallback"""
    logger.info("Calling external service with circuit breaker and fallback")

    # Simulate an external service call that might fail
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("External service is unavailable")

    return {"message": "External service call successful"}

# Add exception handler for circuit breaker
from fastapi_cb import CircuitBreakerOpen

@app.exception_handler(CircuitBreakerOpen)
async def circuit_breaker_open_handler(request, exc):
    """Handle circuit breaker open exception"""
    logger.warning("Circuit breaker is open")
    return JSONResponse(
        status_code=503,
        content={
            "error": "Service temporarily unavailable",
            "message": "The service is currently unavailable due to circuit breaker. Please try again later.",
            "status": "circuit_open"
        }
    )



# Global variable to store the last received booking event
last_received_booking_event = None

@app.post("/pubsub/booking-events")
async def pubsub_booking_events(request: Request):
    """Receives push messages from Pub/Sub subscription."""
    try:
        envelope = await request.json()
        message = envelope['message']

        # Decode the Pub/Sub message data
        data = base64.b64decode(message['data']).decode('utf-8')
        event = json.loads(data)

        # Log the event details
        logger.info(f"Received Pub/Sub message: {event}")

        # Store the last received event
        global last_received_booking_event
        last_received_booking_event = event

        # Acknowledge the message
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.get("/last-booking-event")
def get_last_booking_event():
    """Returns the last received booking event."""
    return {"last_event": last_received_booking_event}
