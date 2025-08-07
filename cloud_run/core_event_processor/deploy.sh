#!/bin/bash

# Deployment script for core event processor Cloud Run service

# Set variables
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="core-event-processor"
REGION="us-central1"

# Build and deploy the Cloud Run service
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated

# Create a Pub/Sub subscription to trigger the Cloud Run service
TOPIC_NAME="core-api.v1.events"
gcloud pubsub subscriptions create $SERVICE_NAME-subscription \
  --topic $TOPIC_NAME \
  --push-endpoint $(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")/process-event \
  --push-auth-service-account $SERVICE_NAME@$PROJECT_ID.iam.gserviceaccount.com
