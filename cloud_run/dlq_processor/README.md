# DLQ Processor for Core-API Service

This service processes messages that have been moved to Dead Letter Queues (DLQs) after failing to be processed by the main event processor.

## Overview

When messages fail to be processed by the main event processor after the maximum number of retries, they are moved to DLQ topics. This service monitors those DLQ topics and processes the failed messages by:

1. Logging the failed message for debugging purposes
2. Sending alerts to notify administrators of the failure
3. Storing the message for manual intervention

## DLQ Topics

The following DLQ topics are monitored by this service:

- `booking-created-dlq`
- `booking-cancelled-dlq`
- `booking-updated-dlq`

## Endpoints

- `GET /` - Health check endpoint
- `POST /process-dlq-message` - Process DLQ messages

## Deployment

To deploy this service, run the deployment script:

```bash
./deploy.sh
```

## Configuration

The service can be configured using the following environment variables:

- `ALERT_EMAIL` - Email address to send alerts to
- `SMTP_SERVER` - SMTP server for sending email alerts
- `SMTP_PORT` - SMTP port
- `SMTP_USER` - SMTP username
- `SMTP_PASSWORD` - SMTP password

## Manual Intervention

Failed messages are stored for manual intervention. In a production environment, this would typically involve:

1. Storing the message in a database for review
2. Providing an interface for administrators to view and process failed messages
3. Allowing administrators to retry or discard failed messages
