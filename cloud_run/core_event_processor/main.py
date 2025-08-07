import json
import logging
from typing import Dict, Any
from flask import Flask, request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.route("/process-event", methods=["POST"])
def process_event():
    """Endpoint to process Pub/Sub push messages"""
    try:
        # Get the Pub/Sub message
        envelope = request.get_json()
        
        # Validate the envelope
        if not envelope:
            return {"error": "No Pub/Sub message received"}, 400
        
        if "message" not in envelope:
            return {"error": "Invalid Pub/Sub message format"}, 400
        
        # Extract the message data
        message = envelope["message"]
        if "data" not in message:
            return {"error": "No data in Pub/Sub message"}, 400
        
        # Decode and parse the message data
        message_data = json.loads(message["data"])
        
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
        
        return ("", 204)  # Return 204 No Content for successful processing
        
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        return {"error": str(e)}, 500

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
