#!/bin/bash

# Deployment script for core event processor Cloud Function

# Set variables
PROJECT_ID="your-gcp-project-id"
FUNCTION_NAME="core-event-processor"
TOPIC_NAME="core-api.v1.events"
REGION="us-central1"

# Deploy the Cloud Function
gcloud functions deploy $FUNCTION_NAME \
  --runtime python39 \
  --trigger-topic $TOPIC_NAME \
  --entry-point process_core_event \
  --source . \
  --region $REGION \
  --project $PROJECT_ID
