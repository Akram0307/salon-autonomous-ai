import json
from google.cloud import pubsub_v1
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.subscriber = pubsub_v1.SubscriberClient()
        self.handlers = {}
    
    def register_handler(
        self, 
        event_type: str, 
        version: str, 
        handler: Callable[[Dict[str, Any]], None]
    ):
        """Register a handler for a specific event type and version"""
        key = f"{event_type}:{version}"
        self.handlers[key] = handler
    
    def subscribe(
        self, 
        domain: str, 
        version: str, 
        subscription_id: str
    ):
        """Subscribe to a versioned Pub/Sub topic and start listening for events"""
        # Create topic and subscription names following the pattern
        topic_name = f"{domain}.v{version}.events"
        topic_path = self.subscriber.topic_path(self.project_id, topic_name)
        subscription_path = self.subscriber.subscription_path(self.project_id, subscription_id)
        
        # Create subscription if it doesn't exist
        try:
            self.subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )
        except Exception as e:
            # Subscription might already exist
            logger.info(f"Subscription may already exist: {e}")
        
        # Define the callback function
        def callback(message):
            try:
                # Decode and parse the message
                event = json.loads(message.data.decode("utf-8"))
                
                # Extract event details
                event_type = event.get("type")
                event_version = event.get("version")
                correlation_id = event.get("correlation_id")
                
                logger.info(f"Received event: {event_type} v{event_version} (correlation_id: {correlation_id})")
                
                # Find and execute the appropriate handler
                handler_key = f"{event_type}:{event_version}"
                if handler_key in self.handlers:
                    self.handlers[handler_key](event)
                    message.ack()
                else:
                    logger.warning(f"No handler registered for {handler_key}")
                    # Try to find a handler for a compatible version
                    # This is where backward compatibility logic would be implemented
                    message.nack()
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                message.nack()
        
        # Start listening for messages
        streaming_pull_future = self.subscriber.subscribe(subscription_path, callback=callback)
        logger.info(f"Listening for messages on {subscription_path}")
        
        return streaming_pull_future

def get_event_consumer(project_id: str) -> EventConsumer:
    """Factory function to get an event consumer instance"""
    return EventConsumer(project_id)
