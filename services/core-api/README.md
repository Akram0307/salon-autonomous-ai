# Core API Service

This service provides the core API endpoints for the salon booking system with integrated reliability primitives.

## Features

1. **Booking Management System**
   - Create bookings with idempotency protection
   - Event versioning for booking events
   - Saga orchestrator for long-running transactions
   - Dead letter queues (DLQ) for failed messages
   - Circuit breakers to prevent cascading failures

2. **Dialogflow Integration**
   - Webhook endpoint for Dialogflow CX
   - Intent processing for user requests
   - Integration with booking management system

3. **Firebase Backend**
   - Authentication and authorization using Firebase Auth
   - CRUD operations on Firestore collections
   - Real-time updates using Firestore listeners

## API Endpoints

### Health Check

- `GET /health` - Health check endpoint

### Booking Management

- `POST /bookings` - Create a new booking with idempotency protection

### Dialogflow Integration

- `POST /dialogflow/webhook` - Receive webhooks from Dialogflow CX

### Firebase Backend

- `GET /firebase/data/{collection}/{document}` - Get a document from Firestore
- `POST /firebase/data/{collection}/{document}` - Set a document in Firestore
- `GET /firebase/data/{collection}` - List documents in a Firestore collection

### Reliability Primitives Examples

- `GET /external-service-call` - Example endpoint with circuit breaker
- `GET /external-service-call-with-fallback` - Example endpoint with circuit breaker and fallback

## Reliability Primitives

### Idempotency

The booking creation endpoint uses idempotency keys to ensure requests are processed only once.
Clients should include an `Idempotency-Key` header in their requests.

### Circuit Breaker

The external service call endpoints demonstrate the use of circuit breakers to prevent cascading failures.

### Saga Orchestrator

The booking creation endpoint integrates with the saga orchestrator for long-running transactions.

## Authentication

Firebase endpoints require authentication using Firebase Auth.
Clients should include an `Authorization: Bearer <token>` header with a valid Firebase ID token.

## Environment Variables

- `PROJECT_ID` - Google Cloud Project ID
- `LOCATION` - Google Cloud Location
- `WORKFLOW_NAME` - Saga Orchestrator Workflow Name

## Dependencies

- FastAPI
- Uvicorn
- Google Cloud Pub/Sub
- Google Cloud Secret Manager
- Google Cloud Firestore
- Google Cloud Dialogflow CX
- Firebase Admin
- FastAPI-CB (Circuit Breaker)

## Running the Service

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```
