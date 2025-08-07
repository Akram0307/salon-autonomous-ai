import json
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_core_event(event: Dict[str, Any], context):
    """Cloud Function to process core-api events from Pub/Sub"""
    try:
        # Decode the Pub/Sub message
        if 'data' in event:
            message_data = json.loads(event['data'].decode('utf-8'))
        else:
            message_data = {}
        
        # Extract event details
        event_type = message_data.get('type')
        event_version = message_data.get('version')
        correlation_id = message_data.get('correlation_id')
        payload = message_data.get('payload', {})
        
        logger.info(f"Processing {event_type} v{event_version} event (correlation_id: {correlation_id})")
        
        # Process based on event type
        if event_type == 'booking_created':
            process_booking_created(payload, correlation_id)
        elif event_type == 'customer_updated':
            process_customer_updated(payload, correlation_id)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            
        logger.info(f"Successfully processed event {event_type} (correlation_id: {correlation_id})")
        
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        # Re-raise the exception to trigger retry mechanism
        raise

def process_booking_created(payload: Dict[str, Any], correlation_id: str):
    """Process a booking created event"""
    booking_id = payload.get('booking_id')
    customer_id = payload.get('customer_id')
    timestamp = payload.get('timestamp')
    
    logger.info(f"Booking created: {booking_id} for customer {customer_id} at {timestamp}")
    
    # Here you would implement the business logic for handling a booking creation
    # This might include:
    # - Sending notifications
    # - Updating analytics
    # - Triggering other workflows
    # - etc.
    
    # Example: Send a notification
    send_booking_notification(booking_id, customer_id)

def process_customer_updated(payload: Dict[str, Any], correlation_id: str):
    """Process a customer updated event"""
    customer_id = payload.get('customer_id')
    action = payload.get('action')
    timestamp = payload.get('timestamp')
    
    logger.info(f"Customer {customer_id} updated with action {action} at {timestamp}")
    
    # Here you would implement the business logic for handling a customer update
    # This might include:
    # - Updating customer data in other systems
    # - Sending notifications
    # - Triggering other workflows
    # - etc.

def send_booking_notification(booking_id: str, customer_id: str):
    """Send a notification about a booking creation"""
    # This is a placeholder for the actual notification logic
    logger.info(f"Sending notification for booking {booking_id} to customer {customer_id}")
