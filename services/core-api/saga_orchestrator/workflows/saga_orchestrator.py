from google.cloud import workflows_v1
from google.cloud.workflows import executions_v1
from google.cloud.workflows.executions_v1 import Execution
import json
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    def __init__(self, project_id: str, location: str, workflow_name: str):
        """Initialize the Saga Orchestrator with GCP project details."""
        self.project_id = project_id
        self.location = location
        self.workflow_name = workflow_name
        
        # Initialize clients
        self.workflows_client = workflows_v1.WorkflowsClient()
        self.executions_client = executions_v1.ExecutionsClient()
        
        # Build workflow name
        self.workflow_path = self.workflows_client.workflow_path(
            project_id, location, workflow_name
        )
    
    def execute_saga(self, saga_id: str = None, steps: List[Dict[str, Any]] = None) -> str:
        """Execute a saga workflow with the provided steps."""
        if not saga_id:
            saga_id = str(uuid.uuid4())
        
        # Prepare the execution arguments
        arguments = {
            "saga_id": saga_id,
            "steps": steps or []
        }
        
        # Create execution request
        execution = Execution()
        execution.argument = json.dumps(arguments)
        
        # Build parent path
        parent = self.executions_client.workflow_path(
            self.project_id, self.location, self.workflow_name
        )
        
        try:
            # Start the execution
            response = self.executions_client.create_execution(
                parent=parent,
                execution=execution
            )
            logger.info(f"Started saga execution: {response.name}")
            return response.name
        except Exception as e:
            logger.error(f"Failed to start saga execution: {str(e)}")
            raise
    
    def get_execution_status(self, execution_name: str) -> Dict[str, Any]:
        """Get the status of a saga execution."""
        try:
            response = self.executions_client.get_execution(name=execution_name)
            return {
                "name": response.name,
                "state": response.state.name,
                "start_time": response.start_time,
                "end_time": response.end_time,
                "result": response.result,
                "error": response.error
            }
        except Exception as e:
            logger.error(f"Failed to get execution status: {str(e)}")
            raise
    
    def cancel_execution(self, execution_name: str) -> bool:
        """Cancel a running saga execution."""
        try:
            response = self.executions_client.cancel_execution(name=execution_name)
            logger.info(f"Cancelled execution: {execution_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel execution: {str(e)}")
            return False

# Example usage:
# saga_orchestrator = SagaOrchestrator(
#     project_id="your-project-id",
#     location="us-central1",
#     workflow_name="saga-orchestrator"
# )
#
# steps = [
#     {
#         "name": "create_booking",
#         "execute_url": "https://booking-service-url/execute",
#         "execute_payload": {"action": "create", "data": "..."},
#         "compensate_url": "https://booking-service-url/compensate",
#         "compensate_payload": {"action": "cancel", "data": "..."}
#     },
#     {
#         "name": "process_payment",
#         "execute_url": "https://payment-service-url/execute",
#         "execute_payload": {"action": "charge", "data": "..."},
#         "compensate_url": "https://payment-service-url/compensate",
#         "compensate_payload": {"action": "refund", "data": "..."}
#     }
# ]
#
# execution_name = saga_orchestrator.execute_saga(steps=steps)
# print(f"Saga started: {execution_name}")
