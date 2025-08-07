from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import json
import logging
from datetime import datetime
import asyncio

# Import reliability primitives
from app.idempotency.decorator import idempotent
from app.circuit_breaker.circuit_breaker import with_circuit_breaker, fallback_handler
from saga_orchestrator.workflows.saga_orchestrator import SagaOrchestrator

# Import Google Cloud clients
from google.cloud import pubsub_v1, firestore
from google.cloud.pubsub_v1 import types
from google.cloud.pubsub_v1.subscriber.message import Message
from google.cloud.pubsub_v1.publisher.futures import Future
from google.oauth2 import service_account

# Import Dialogflow CX
from google.cloud.dialogflowcx_v3beta1 import services
from google.cloud.dialogflowcx_v3beta1 import types as df_types

# Import Firebase Admin
import firebase_admin
from firebase_admin import credentials, auth, firestore as firebase_firestore

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Core API Service", version="1.0.0")

# Initialize Firebase Admin SDK
try:
    # Initialize with default credentials if available
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
    # Continue without Firebase if initialization fails

# Initialize Firestore client
try:
    db = firestore.Client()
    logger.info("Firestore client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firestore client: {str(e)}")
    db = None

# Initialize Pub/Sub publisher
try:
    publisher = pubsub_v1.PublisherClient()
    logger.info("Pub/Sub publisher client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Pub/Sub publisher client: {str(e)}")
    publisher = None

# Initialize Saga Orchestrator
try:
    # These would typically come from environment variables
    PROJECT_ID = "your-project-id"  # Replace with actual project ID
    LOCATION = "us-central1"        # Replace with actual location
    WORKFLOW_NAME = "saga-orchestrator"  # Replace with actual workflow name
    
    # Only initialize if we have the required values
    if PROJECT_ID != "your-project-id":
        saga_orchestrator = SagaOrchestrator(
            project_id=PROJECT_ID,
            location=LOCATION,
            workflow_name=WORKFLOW_NAME
        )
        logger.info("Saga Orchestrator initialized successfully")
    else:
        saga_orchestrator = None
        logger.warning("Saga Orchestrator not initialized - missing configuration")
except Exception as e:
    logger.error(f"Failed to initialize Saga Orchestrator: {str(e)}")
    saga_orchestrator = None

# Models
class BookingRequest(BaseModel):
    service_id: str
    customer_name: str
    date: str
    time: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    message: str

class DialogflowWebhookRequest(BaseModel):
    detectIntentResponse: Dict[str, Any]
    
# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0"}

# Booking Management System
@app.post("/bookings", response_model=BookingResponse)
@idempotent(ttl_seconds=3600)  # 1 hour TTL
async def create_booking(booking: BookingRequest, request: Request):
    """Create a new booking with idempotency protection"""
    try:
        # Generate a unique booking ID
        booking_id = str(uuid.uuid4())
        
        # Create booking data
        booking_data = {
            "booking_id": booking_id,
            "service_id": booking.service_id,
            "customer_name": booking.customer_name,
            "date": booking.date,
            "time": booking.time,
            "customer_email": booking.customer_email,
            "customer_phone": booking.customer_phone,
            "status": "confirmed",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # If we have a database connection, save the booking
        if db is not None:
            try:
                doc_ref = db.collection('bookings').document(booking_id)
                doc_ref.set(booking_data)
                logger.info(f"Booking {booking_id} saved to Firestore")
            except Exception as e:
                logger.error(f"Failed to save booking to Firestore: {str(e)}")
                # Don't fail the request if we can't save to database
        
        # Publish booking event to Pub/Sub with versioning
        if publisher is not None:
            try:
                # Add event versioning
                event_data = {
                    "version": "1.0",
                    "event_type": "booking_created",
                    "data": booking_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Convert to JSON
                message_data = json.dumps(event_data).encode('utf-8')
                
                # Publish to topic (you would replace with your actual topic)
                topic_path = publisher.topic_path("your-project-id", "bookings-v1")  # Replace with actual project ID and topic
                
                # Publish message
                future = publisher.publish(topic_path, message_data)
                result = future.result()
                logger.info(f"Booking event published to Pub/Sub: {result}")
            except Exception as e:
                logger.error(f"Failed to publish booking event to Pub/Sub: {str(e)}")
                # Don't fail the request if we can't publish to Pub/Sub
        
        # Use saga orchestrator for long-running transactions if available
        if saga_orchestrator is not None:
            try:
                # Define saga steps (this is a simplified example)
                steps = [
                    {
                        "name": "create_booking",
                        "execute_url": "https://booking-service-url/execute",
                        "execute_payload": {"action": "create", "data": booking_data},
                        "compensate_url": "https://booking-service-url/compensate",
                        "compensate_payload": {"action": "cancel", "data": booking_data}
                    }
                    # Add more steps as needed for payment, CRM update, etc.
                ]
                
                # Execute the saga
                execution_name = saga_orchestrator.execute_saga(steps=steps)
                logger.info(f"Saga started for booking {booking_id}: {execution_name}")
            except Exception as e:
                logger.error(f"Failed to start saga for booking {booking_id}: {str(e)}")
                # Don't fail the request if we can't start the saga
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            message=f"Booking {booking_id} created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create booking: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create booking")

# Dialogflow Integration
@app.post("/dialogflow/webhook")
async def dialogflow_webhook(webhook_request: DialogflowWebhookRequest):
    """Receive webhooks from Dialogflow CX and process user intents"""
    try:
        # Extract intent and parameters from Dialogflow response
        detect_intent_response = webhook_request.detectIntentResponse
        
        # Log the full request for debugging
        logger.info(f"Dialogflow webhook request: {json.dumps(detect_intent_response, indent=2)}")
        
        # Extract intent information
        if "queryResult" in detect_intent_response and "intent" in detect_intent_response["queryResult"]:
            intent_name = detect_intent_response["queryResult"]["intent"].get("displayName", "unknown")
            logger.info(f"Detected intent: {intent_name}")
            
            # Process different intents
            if intent_name == "booking.service":  # Example intent for booking a service
                # Extract parameters
                parameters = detect_intent_response["queryResult"].get("parameters", {})
                
                # Extract booking information
                service_name = parameters.get("service", "")
                date = parameters.get("date", "")
                time = parameters.get("time", "")
                customer_name = parameters.get("customer_name", "")
                
                # Create booking
                booking_request = BookingRequest(
                    service_id=service_name,
                    customer_name=customer_name,
                    date=date,
                    time=time
                )
                
                # Call our booking creation endpoint
                # In a real implementation, you might want to call the function directly
                # or make an internal HTTP request
                booking_response = await create_booking_internal(booking_request)
                
                # Prepare response for Dialogflow
                response_text = f"I've successfully booked your {service_name} appointment for {date} at {time}. Your booking ID is {booking_response.booking_id}."
                
                return {
                    "fulfillment_response": {
                        "messages": [
                            {
                                "text": {
                                    "text": [response_text]
                                }
                            }
                        ]
                    }
                }
            else:
                # Handle other intents
                response_text = "I'm not sure how to handle that request. Can you please rephrase?"
                
                return {
                    "fulfillment_response": {
                        "messages": [
                            {
                                "text": {
                                    "text": [response_text]
                                }
                            }
                        ]
                    }
                }
        else:
            logger.warning("No intent found in Dialogflow webhook request")
            return {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": ["I'm sorry, I didn't understand that. Could you please try again?"]
                            }
                        }
                    ]
                }
            }
    except Exception as e:
        logger.error(f"Failed to process Dialogflow webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process Dialogflow webhook")

# Internal function to create booking (used by Dialogflow webhook)
async def create_booking_internal(booking: BookingRequest):
    """Internal function to create a booking"""
    # Generate a unique booking ID
    booking_id = str(uuid.uuid4())
    
    # Create booking data
    booking_data = {
        "booking_id": booking_id,
        "service_id": booking.service_id,
        "customer_name": booking.customer_name,
        "date": booking.date,
        "time": booking.time,
        "customer_email": booking.customer_email,
        "customer_phone": booking.customer_phone,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # If we have a database connection, save the booking
    if db is not None:
        try:
            doc_ref = db.collection('bookings').document(booking_id)
            doc_ref.set(booking_data)
            logger.info(f"Booking {booking_id} saved to Firestore")
        except Exception as e:
            logger.error(f"Failed to save booking to Firestore: {str(e)}")
    
    return BookingResponse(
        booking_id=booking_id,
        status="confirmed",
        message=f"Booking {booking_id} created successfully"
    )

# Firebase Backend Endpoints
# Dependency to verify Firebase token
async def verify_firebase_token(authorization: str = Header(None)):
    """Verify Firebase ID token and return user info"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token from Authorization header
        token = authorization.split("Bearer ")[1]
        
        # Verify token
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Failed to verify Firebase token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/firebase/data/{collection}/{document}")
async def get_firebase_document(
    collection: str, 
    document: str, 
    user: dict = Depends(verify_firebase_token)
):
    """Get a document from Firestore"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Firestore not initialized")
        
        # Get document
        doc_ref = db.collection(collection).document(document)
        doc = doc_ref.get()
        
        if doc.exists:
            return {"data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logger.error(f"Failed to get document from Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document")

@app.post("/firebase/data/{collection}/{document}")
async def set_firebase_document(
    collection: str, 
    document: str, 
    data: dict,
    user: dict = Depends(verify_firebase_token)
):
    """Set a document in Firestore"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Firestore not initialized")
        
        # Set document
        doc_ref = db.collection(collection).document(document)
        doc_ref.set(data)
        
        return {"message": "Document saved successfully"}
    except Exception as e:
        logger.error(f"Failed to set document in Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save document")

@app.get("/firebase/data/{collection}")
async def list_firebase_documents(
    collection: str,
    user: dict = Depends(verify_firebase_token)
):
    """List documents in a Firestore collection"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Firestore not initialized")
        
        # List documents
        docs = db.collection(collection).stream()
        documents = []
        
        for doc in docs:
            documents.append({"id": doc.id, "data": doc.to_dict()})
        
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Failed to list documents in Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

# Example endpoint with circuit breaker
@app.get("/external-service-call")
@with_circuit_breaker
async def call_external_service():
    """Example endpoint that demonstrates circuit breaker usage"""
    # Simulate an external service call
    # In a real implementation, this would call an actual external service
    await asyncio.sleep(1)
    return {"message": "External service call successful"}

@app.get("/external-service-call-with-fallback")
@with_circuit_breaker
async def call_external_service_with_fallback():
    """Example endpoint that demonstrates circuit breaker with fallback"""
    # Simulate a failing external service call
    raise Exception("External service is unavailable")

# Exception handler for circuit breaker
@app.exception_handler(Exception)
async def circuit_breaker_exception_handler(request, exc):
    """Handle circuit breaker exceptions with fallback"""
    if "CircuitBreakerOpen" in str(type(exc)):
        fallback_response = fallback_handler(exc)
        return JSONResponse(status_code=503, content=fallback_response)
    else:
        # Re-raise the exception if it's not a circuit breaker exception
        raise exc

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
