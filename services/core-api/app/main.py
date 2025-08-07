from fastapi import FastAPI, Request, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import logging
import json
from datetime import datetime

# Import reliability primitives
from .idempotency.decorator import idempotent
from .circuit_breaker.circuit_breaker import with_circuit_breaker, fallback_handler
from fastapi.responses import JSONResponse

# Import saga orchestrator
from ..saga_orchestrator.workflows.saga_orchestrator import SagaOrchestrator

# Import the events router
from .events.example_usage import router as events_router

# Firebase imports
import firebase_admin
from firebase_admin import auth, credentials, firestore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Import circuit breaker for external service calls
app = FastAPI()

# Include the events router
app.include_router(events_router, prefix="/events", tags=["events"])

# Example data model
class BookingRequest(BaseModel):
    service_id: str
    customer_name: str
    date: str
    time: str
    notes: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    service_id: str
    customer_name: str
    date: str
    time: str
    status: str
    notes: Optional[str] = None

# Dialogflow webhook model
class DialogflowWebhookRequest(BaseModel):
    responseId: str
    session: str
    queryResult: Dict[str, Any]
    originalDetectIntentRequest: Optional[Dict[str, Any]] = None

# Firebase authentication dependency
def verify_firebase_token(request: Request):
    """Verify Firebase ID token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from Bearer header
        token = auth_header.split('Bearer ')[1]
        
        # Verify token
        decoded_token = auth.verify_id_token(token)
        
        # Add user info to request state
        request.state.user = decoded_token
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Enhanced booking endpoint with saga orchestrator
@app.post("/bookings", response_model=BookingResponse)
@idempotent(ttl_seconds=3600)  # 1 hour TTL
async def create_booking(booking: BookingRequest, request: Request):
    """Create a booking with idempotency support and saga orchestration"""
    logger.info(f"Processing booking request for {booking.customer_name}")
    
    # Initialize saga orchestrator
    saga_orchestrator = SagaOrchestrator(
        project_id="your-gcp-project-id",
        location="us-central1",
        workflow_name="booking-saga"
    )
    
    # Define saga steps for booking + payment + CRM update
    steps = [
        {
            "name": "create_booking",
            "execute_url": "https://booking-service-url/execute",
            "execute_payload": {
                "action": "create",
                "data": booking.dict()
            },
            "compensate_url": "https://booking-service-url/compensate",
            "compensate_payload": {
                "action": "cancel",
                "booking_id": "{{booking_id}}"
            }
        },
        {
            "name": "process_payment",
            "execute_url": "https://payment-service-url/execute",
            "execute_payload": {
                "action": "charge",
                "amount": 50.0,  # This would come from pricing service in a real implementation
                "customer_name": booking.customer_name
            },
            "compensate_url": "https://payment-service-url/compensate",
            "compensate_payload": {
                "action": "refund",
                "transaction_id": "{{transaction_id}}"
            }
        },
        {
            "name": "update_crm",
            "execute_url": "https://crm-service-url/execute",
            "execute_payload": {
                "action": "add_booking",
                "customer_name": booking.customer_name,
                "booking_id": "{{booking_id}}",
                "service_id": booking.service_id
            },
            "compensate_url": "https://crm-service-url/compensate",
            "compensate_payload": {
                "action": "remove_booking",
                "booking_id": "{{booking_id}}"
            }
        }
    ]
    
    try:
        # Execute the saga
        execution_name = saga_orchestrator.execute_saga(steps=steps)
        logger.info(f"Booking saga started: {execution_name}")
        
        # Create a booking ID
        booking_id = str(uuid.uuid4())
        
        # Create response
        response_data = BookingResponse(
            booking_id=booking_id,
            service_id=booking.service_id,
            customer_name=booking.customer_name,
            date=booking.date,
            time=booking.time,
            status="confirmed",
            notes=booking.notes
        )
        
        logger.info(f"Booking created with ID: {booking_id}")
        
        return JSONResponse(content=response_data.dict(), status_code=201)
    except Exception as e:
        logger.error(f"Failed to create booking: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create booking")

# Dialogflow webhook endpoint
@app.post("/dialogflow/webhook")
async def dialogflow_webhook(request: DialogflowWebhookRequest):
    """Process Dialogflow CX webhook requests"""
    logger.info(f"Received Dialogflow webhook request: {request.responseId}")
    
    try:
        # Extract intent and parameters
        intent = request.queryResult.get("intent", {}).get("displayName", "unknown")
        parameters = request.queryResult.get("parameters", {})
        
        # Process based on intent
        if intent == "book.service":
            # Extract booking information from parameters
            service_id = parameters.get("service_id")
            customer_name = parameters.get("customer_name")
            date = parameters.get("date")
            time = parameters.get("time")
            notes = parameters.get("notes", "")
            
            # Create booking request
            booking_request = BookingRequest(
                service_id=service_id,
                customer_name=customer_name,
                date=date,
                time=time,
                notes=notes
            )
            
            # In a real implementation, this would call the actual booking endpoint
            # For now, we'll simulate the booking creation
            booking_id = str(uuid.uuid4())
            
            # Return fulfillment response to Dialogflow
            return {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": [f"I've successfully booked your appointment for {service_id} on {date} at {time}."]
                            }
                        }
                    ]
                },
                "session_info": {
                    "parameters": {
                        "booking_id": booking_id
                    }
                }
            }
        
        # Default response for unhandled intents
        return {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": ["I didn't understand that request. Could you please try again?"]
                        }
                    }
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error processing Dialogflow webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing webhook")

# Firebase authentication endpoint
@app.get("/firebase/verify-token")
async def verify_token(decoded_token: dict = Depends(verify_firebase_token)):
    """Verify Firebase authentication token"""
    return {"status": "authenticated", "user": decoded_token}

# Firestore data interaction endpoints
@app.post("/firestore/{collection}")
async def create_firestore_document(collection: str, data: dict, request: Request, decoded_token: dict = Depends(verify_firebase_token)):
    """Create a document in Firestore"""
    try:
        # Add tenant_id from token to document data
        tenant_id = decoded_token.get('tenant_id')
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID not found in token")
        
        data['tenant_id'] = tenant_id
        data['created_at'] = datetime.utcnow().isoformat()
        
        # Create document in Firestore
        doc_ref = db.collection(collection).document()
        doc_ref.set(data)
        
        return {"id": doc_ref.id, "data": data}
    except Exception as e:
        logger.error(f"Error creating Firestore document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating document")

@app.get("/firestore/{collection}/{document_id}")
async def get_firestore_document(collection: str, document_id: str, request: Request, decoded_token: dict = Depends(verify_firebase_token)):
    """Retrieve a document from Firestore"""
    try:
        # Get tenant_id from token
        tenant_id = decoded_token.get('tenant_id')
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID not found in token")
        
        # Retrieve document from Firestore
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = doc.to_dict()
        
        # Check if document belongs to tenant
        if doc_data.get('tenant_id') != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {"id": doc.id, "data": doc_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Firestore document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving document")

@app.put("/firestore/{collection}/{document_id}")
async def update_firestore_document(collection: str, document_id: str, data: dict, request: Request, decoded_token: dict = Depends(verify_firebase_token)):
    """Update a document in Firestore"""
    try:
        # Get tenant_id from token
        tenant_id = decoded_token.get('tenant_id')
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID not found in token")
        
        # Retrieve document from Firestore
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = doc.to_dict()
        
        # Check if document belongs to tenant
        if doc_data.get('tenant_id') != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update document
        data['updated_at'] = datetime.utcnow().isoformat()
        doc_ref.update(data)
        
        return {"id": doc.id, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Firestore document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating document")

@app.delete("/firestore/{collection}/{document_id}")
async def delete_firestore_document(collection: str, document_id: str, request: Request, decoded_token: dict = Depends(verify_firebase_token)):
    """Delete a document from Firestore"""
    try:
        # Get tenant_id from token
        tenant_id = decoded_token.get('tenant_id')
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID not found in token")
        
        # Retrieve document from Firestore
        doc_ref = db.collection(collection).document(document_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = doc.to_dict()
        
        # Check if document belongs to tenant
        if doc_data.get('tenant_id') != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete document
        doc_ref.delete()
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Firestore document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting document")

# Example endpoint with circuit breaker
@app.get("/external-service-call")
@with_circuit_breaker
async def call_external_service():
    """Example endpoint that demonstrates circuit breaker usage"""
    logger.info("Calling external service with circuit breaker")

    # Simulate an external service call that might fail
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("External service is unavailable")

    return {"message": "External service call successful"}

# Example endpoint with circuit breaker and fallback
@app.get("/external-service-call-with-fallback")
@with_circuit_breaker
async def call_external_service_with_fallback():
    """Example endpoint that demonstrates circuit breaker with fallback"""
    logger.info("Calling external service with circuit breaker and fallback")

    # Simulate an external service call that might fail
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("External service is unavailable")

    return {"message": "External service call successful"}

# Add exception handler for circuit breaker
from fastapi_cb import CircuitBreakerOpen

@app.exception_handler(CircuitBreakerOpen)
async def circuit_breaker_open_handler(request, exc):
    """Handle circuit breaker open exception"""
    logger.warning("Circuit breaker is open")
    return JSONResponse(
        status_code=503,
        content={
            "error": "Service temporarily unavailable",
            "message": "The service is currently unavailable due to circuit breaker. Please try again later.",
            "status": "circuit_open"
        }
    )
