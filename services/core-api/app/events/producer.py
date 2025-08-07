import json
from datetime import datetime
import uuid
from google.cloud import pubsub_v1
from typing import Dict, Any, Optional

class EventProducer:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
    
    def publish_event(
        self, 
        domain: str, 
        version: str, 
        event_type: str, 
        tenant_id: str, 
        payload: Dict[str, Any], 
        correlation_id: Optional[str] = None
    ) -> str:
        """Publish an event to a versioned Pub/Sub topic"""
        # Create topic name following the pattern: <domain>.v<version>.events
        topic_name = f"{domain}.v{version}.events"
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Create the event message following the standard schema
        event = {
            "type": event_type,
            "version": version,
            "occurred_at": datetime.utcnow().isoformat() + "Z",
            "tenant_id": tenant_id,
            "correlation_id": correlation_id,
            "payload": payload
        }
        
        # Convert to JSON and encode
        message_data = json.dumps(event).encode("utf-8")
        
        # Publish the message
        future = self.publisher.publish(topic_path, message_data)
        message_id = future.result()
        
        return message_id

def get_event_producer(project_id: str) -> EventProducer:
    """Factory function to get an event producer instance"""
    return EventProducer(project_id)
