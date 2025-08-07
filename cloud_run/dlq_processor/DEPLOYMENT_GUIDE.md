# DLQ Processor Deployment Guide

## Prerequisites

1. Ensure you have the Google Cloud SDK installed and authenticated
2. Ensure you have Docker installed
3. Ensure you have the necessary permissions to deploy to Cloud Run and create Pub/Sub subscriptions

## Step 1: Deploy the DLQ Processor to Cloud Run

1. Navigate to the dlq_processor directory:
   ```bash
   cd /root/salon-autonomous-ai/cloud_run/dlq_processor
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. Note the URL of the deployed service. It will be in the format:
   https://dlq-processor-<random-hash>-<region>.a.run.app

## Step 2: Create Push Subscriptions for DLQ Topics

After deploying the DLQ processor, create push subscriptions for each DLQ topic:

```bash
# Replace SERVICE_URL with the actual URL of your deployed DLQ processor service

# Create push subscription for booking-created-dlq
gcloud pubsub subscriptions create booking-created-dlq-sub   --topic=booking-created-dlq   --push-endpoint=SERVICE_URL/process-dlq-message

# Create push subscription for booking-cancelled-dlq
gcloud pubsub subscriptions create booking-cancelled-dlq-sub   --topic=booking-cancelled-dlq   --push-endpoint=SERVICE_URL/process-dlq-message

# Create push subscription for booking-updated-dlq
gcloud pubsub subscriptions create booking-updated-dlq-sub   --topic=booking-updated-dlq   --push-endpoint=SERVICE_URL/process-dlq-message
```

## Configuration

The service can be configured using the following environment variables:

- `ALERT_EMAIL` - Email address to send alerts to
- `SMTP_SERVER` - SMTP server for sending email alerts
- `SMTP_PORT` - SMTP port
- `SMTP_USER` - SMTP username
- `SMTP_PASSWORD` - SMTP password

Update these in the deploy.sh script before deploying.
