# Saga Orchestrator

This module provides a saga orchestrator implementation using Google Cloud Workflows and Cloud Tasks for managing long-running distributed transactions across multiple services.

## Features

- **Cloud Workflows Integration**: Uses Google Cloud Workflows for orchestrating saga steps
- **Compensation Handling**: Automatically executes compensating actions when a step fails
- **Cloud Tasks Integration**: Provides deterministic HTTP retries for external API calls
- **Flexible Configuration**: Supports custom retry policies and scheduling

## Architecture

The saga orchestrator uses a two-layered approach:

1. **Orchestration Layer** (Google Cloud Workflows): Manages the overall flow of the saga, including executing steps and handling compensations
2. **Task Layer** (Google Cloud Tasks): Handles individual HTTP calls with retry mechanisms

## Usage

### Defining Saga Steps

Each step in a saga should include:

- `name`: A descriptive name for the step
- `execute_url`: The URL to call for executing the step
- `execute_payload`: The payload to send when executing the step
- `compensate_url`: The URL to call for compensating the step
- `compensate_payload`: The payload to send when compensating the step

### Example

```python
from saga_orchestrator.workflows.saga_orchestrator import SagaOrchestrator

# Initialize the orchestrator
orchestrator = SagaOrchestrator(
    project_id="your-project-id",
    location="us-central1",
    workflow_name="saga-orchestrator"
)

# Define steps
steps = [
    {
        "name": "create_booking",
        "execute_url": "https://booking-service/execute",
        "execute_payload": {"action": "create", "data": booking_data},
        "compensate_url": "https://booking-service/compensate",
        "compensate_payload": {"action": "cancel", "booking_id": booking_id}
    },
    {
        "name": "process_payment",
        "execute_url": "https://payment-service/execute",
        "execute_payload": {"action": "charge", "amount": amount},
        "compensate_url": "https://payment-service/compensate",
        "compensate_payload": {"action": "refund", "transaction_id": transaction_id}
    }
]

# Execute the saga
execution_name = orchestrator.execute_saga(steps=steps)
```

## Cloud Tasks Integration

For handling retries to external providers:

```python
from saga_orchestrator.tasks.task_manager import TaskManager

task_manager = TaskManager(
    project_id="your-project-id",
    location_id="us-central1",
    queue_id="saga-tasks"
)

task_response = task_manager.create_retry_task(
    url="https://external-provider/api/endpoint",
    payload={"data": "value"},
    max_attempts=5
)
```

## Deployment

1. Deploy the Cloud Workflows definition in `workflows/saga_orchestrator.yaml`
2. Create a Cloud Tasks queue named `saga-tasks`
3. Ensure the service account has the necessary permissions for Cloud Workflows and Cloud Tasks

## Security

- All HTTP calls use OIDC authentication
- Secrets are managed through Google Secret Manager
- IAM permissions are configured with least privilege principle
