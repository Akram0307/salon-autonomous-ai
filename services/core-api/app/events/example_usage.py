from fastapi import APIRouter
from .producer import get_event_producer
from ..idempotency.decorator import idempotent
import os

# Create a router for event-related endpoints
router = APIRouter()

# Get the project ID from environment variables
PROJECT_ID = os.getenv("PROJECT_ID", "your-gcp-project-id")

# Get an event producer instance
producer = get_event_producer(PROJECT_ID)

@router.post("/trigger-booking-event")
@idempotent(ttl_seconds=3600)
async def trigger_booking_event(booking_id: str, customer_id: str):
    """Trigger a booking event when a booking is created"""
    # Publish a booking created event to the core-api.v1.events topic
    message_id = producer.publish_event(
        domain="core-api",
        version="1",
        event_type="booking_created",
        tenant_id="default",
        payload={
            "booking_id": booking_id,
            "customer_id": customer_id,
            "timestamp": "2025-08-07T14:30:00Z"
        }
    )
    
    return {"message": "Event published", "message_id": message_id}

@router.post("/trigger-customer-event")
@idempotent(ttl_seconds=3600)
async def trigger_customer_event(customer_id: str, action: str):
    """Trigger a customer event when customer data is updated"""
    # Publish a customer event to the core-api.v1.events topic
    message_id = producer.publish_event(
        domain="core-api",
        version="1",
        event_type="customer_updated",
        tenant_id="default",
        payload={
            "customer_id": customer_id,
            "action": action,
            "timestamp": "2025-08-07T14:30:00Z"
        }
    )
    
    return {"message": "Event published", "message_id": message_id}
