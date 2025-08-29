from flask import Flask, request, jsonify
from .workflows.saga_orchestrator import SagaOrchestrator
from .tasks.task_manager import TaskManager
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the saga orchestrator
# Note: In a real application, these values should come from environment variables
saga_orchestrator = SagaOrchestrator(
    project_id="your-gcp-project-id",
    location="us-central1",
    workflow_name="saga-orchestrator"
)

task_manager = TaskManager(
    project_id="your-gcp-project-id",
    location_id="us-central1",
    queue_id="saga-tasks"
)

@app.route('/start-booking-saga', methods=['POST'])
def start_booking_saga():
    """Start a booking saga with multiple steps."""
    try:
        # Get request data
        data = request.get_json()
        
        # Define saga steps
        steps = [
            {
                "name": "create_booking",
                "execute_url": "https://booking-service-url/execute",
                "execute_payload": {
                    "action": "create",
                    "data": data.get("booking_data", {})
                },
                "compensate_url": "https://booking-service-url/compensate",
                "compensate_payload": {
                    "action": "cancel",
                    "booking_id": "{{booking_id}}"  # This would be replaced with actual booking ID
                }
            },
            {
                "name": "process_payment",
                "execute_url": "https://payment-service-url/execute",
                "execute_payload": {
                    "action": "charge",
                    "amount": data.get("amount", 0),
                    "payment_method": data.get("payment_method", {})
                },
                "compensate_url": "https://payment-service-url/compensate",
                "compensate_payload": {
                    "action": "refund",
                    "transaction_id": "{{transaction_id}}"  # This would be replaced with actual transaction ID
                }
            },
            {
                "name": "send_confirmation",
                "execute_url": "https://notification-service-url/execute",
                "execute_payload": {
                    "action": "send_confirmation",
                    "customer_email": data.get("customer_email"),
                    "booking_details": data.get("booking_data", {})
                },
                "compensate_url": "https://notification-service-url/compensate",
                "compensate_payload": {
                    "action": "send_cancellation",
                    "customer_email": data.get("customer_email"),
                    "booking_id": "{{booking_id}}"
                }
            }
        ]
        
        # Execute the saga
        execution_name = saga_orchestrator.execute_saga(steps=steps)
        
        return jsonify({
            "status": "success",
            "message": "Saga started successfully",
            "execution_name": execution_name
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to start booking saga: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/create-retry-task', methods=['POST'])
def create_retry_task():
    """Create a task with retry configuration for external API calls."""
    try:
        data = request.get_json()
        
        # Create a task with custom retry configuration
        task_response = task_manager.create_retry_task(
            url=data.get("url"),
            payload=data.get("payload"),
            max_attempts=data.get("max_attempts", 5)
        )
        
        return jsonify({
            "status": "success",
            "message": "Task created successfully",
            "task_name": task_response.name
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to create retry task: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
