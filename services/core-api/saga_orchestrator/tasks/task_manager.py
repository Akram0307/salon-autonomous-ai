from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, project_id, location_id, queue_id):
        """Initialize the TaskManager with GCP project details."""
        self.project_id = project_id
        self.location_id = location_id
        self.queue_id = queue_id
        self.client = tasks_v2.CloudTasksClient()
        self.parent = self.client.queue_path(project_id, location_id, queue_id)
    
    def create_http_task(self, url, payload=None, method='POST', schedule_time=None, max_attempts=3):
        """Create an HTTP task with optional scheduling and retry configuration."""
        # Create the task
        task = {
            "http_request": {
                "url": url,
                "http_method": method,
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        }
        
        # Add payload if provided
        if payload:
            task["http_request"]["body"] = json.dumps(payload).encode()
        
        # Set schedule time if provided
        if schedule_time:
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(schedule_time)
            task["schedule_time"] = timestamp
        
        # Configure retry policy
        task["dispatch_deadline"] = timestamp_pb2.Duration(seconds=300)  # 5 minutes
        
        # Create the request
        request = {
            "parent": self.parent,
            "task": task
        }
        
        # Create the task
        try:
            response = self.client.create_task(request=request)
            logger.info(f"Created task: {response.name}")
            return response
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    def create_delayed_task(self, url, payload=None, delay_seconds=60, method='POST'):
        """Create a task that will be executed after a delay."""
        schedule_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        return self.create_http_task(url, payload, method, schedule_time)
    
    def create_retry_task(self, url, payload=None, max_attempts=5, method='POST'):
        """Create a task with custom retry configuration."""
        task = {
            "http_request": {
                "url": url,
                "http_method": method,
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "dispatch_deadline": timestamp_pb2.Duration(seconds=300)
        }
        
        # Add payload if provided
        if payload:
            task["http_request"]["body"] = json.dumps(payload).encode()
        
        # Configure retry policy
        task["retry_config"] = {
            "max_attempts": max_attempts,
            "min_backoff": timestamp_pb2.Duration(seconds=1),
            "max_backoff": timestamp_pb2.Duration(seconds=3600),
            "max_doublings": 16
        }
        
        request = {
            "parent": self.parent,
            "task": task
        }
        
        try:
            response = self.client.create_task(request=request)
            logger.info(f"Created retry task: {response.name}")
            return response
        except Exception as e:
            logger.error(f"Failed to create retry task: {str(e)}")
            raise
