#!/bin/bash

# Exit on any error
set -e

# Set variables
PROJECT_ID="salon-autonomous-ai-467811"
SERVICE_NAME="dlq-processor"
REGION="asia-south1"

# Build the Docker image
echo "Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Push the Docker image to Google Container Registry
echo "Pushing Docker image to GCR..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy the service to Cloud Run
echo "Deploying service to Cloud Run..."
gcloud run deploy $SERVICE_NAME   --image gcr.io/$PROJECT_ID/$SERVICE_NAME   --platform managed   --region $REGION   --allow-unauthenticated   --set-env-vars ALERT_EMAIL=admin@example.com,SMTP_SERVER=smtp.example.com,SMTP_PORT=587,SMTP_USER=user@example.com,SMTP_PASSWORD=password

echo "Deployment completed successfully!"
