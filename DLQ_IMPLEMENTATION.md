# Dead Letter Queue (DLQ) Implementation

## Overview

This document describes the Dead Letter Queue (DLQ) implementation for the core-api service. DLQs are used to handle messages that fail to be processed after a certain number of retries.

## Implementation Details

### DLQ Topics

For each main topic, a corresponding DLQ topic is created:

- `booking-created` -> `booking-created-dlq`
- `booking-cancelled` -> `booking-cancelled-dlq`
- `booking-updated` -> `booking-updated-dlq`

### Subscriptions with Dead Letter Policies

Subscriptions are created with dead letter policies that specify:

- The DLQ topic where failed messages should be sent
- Maximum delivery attempts (5)
- Retry policy with minimum backoff of 10s and maximum backoff of 600s

### DLQ Processor Service

A Cloud Run service (`dlq-processor`) is implemented to process messages from the DLQ topics. This service:

1. Receives messages from DLQ topics via push subscriptions
2. Logs the failed message for debugging purposes
3. Sends alerts to notify administrators of the failure
4. Stores the message for manual intervention

## Deployment

1. The pubsub module in Terraform creates the necessary topics and subscriptions with DLQ policies
2. The dlq-processor Cloud Run service is deployed using the deployment script
3. Push subscriptions are created to send messages from DLQ topics to the dlq-processor service

## Configuration

The dlq-processor service can be configured using environment variables for alerting:

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
