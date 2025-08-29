# Event Versioning for Core-API Service

This document describes the implementation of event versioning for the core-api service using Google Cloud Pub/Sub.

## Versioning Scheme

Events are versioned using topics namespaced per domain and version:

```
<domain>.v<version>.events
```

For example:
- `core-api.v1.events`
- `core-api.v2.events`

## Event Schema

All events follow a standard schema:

```json
{
  "type": "string",
  "version": "string",
  "occurred_at": "string (ISO 8601 format)",
  "tenant_id": "string",
  "correlation_id": "string",
  "payload": "object"
}
```

## Components

### Event Producer

The event producer is located in `services/core-api/app/events/producer.py` and provides a simple interface to publish events to versioned topics.

### Event Consumer

The event consumer is located in `services/core-api/app/events/consumer.py` and provides a framework for consuming events from versioned topics.

### Example Usage

An example of how to use the event producer is provided in `services/core-api/app/events/example_usage.py`.

## Event Processing

Event processing can be implemented using either:

1. **Cloud Functions** - Located in `cloud_functions/core_event_processor/`
2. **Cloud Run Services** - Located in `cloud_run/core_event_processor/`

Both examples demonstrate how to process events from the `core-api.v1.events` topic.

## Deployment

### Cloud Function

To deploy the Cloud Function:

```bash
./cloud_functions/core_event_processor/deploy.sh
```

### Cloud Run Service

To deploy the Cloud Run service:

```bash
./cloud_run/core_event_processor/deploy.sh
```

## Backward Compatibility

The implementation ensures backward compatibility by:

1. Using versioned topics to separate different event versions
2. Providing a consumer framework that can handle multiple event versions
3. Allowing for graceful degradation when new event versions are introduced

When introducing a new event version:

1. Create a new topic with the new version number
2. Update producers to publish to the new topic
3. Update consumers to handle events from both the old and new topics
4. Gradually migrate consumers to the new version
5. Deprecate the old topic after all producers have been migrated

## Adding New Event Types

To add a new event type:

1. Define the event structure in the payload of the standard event schema
2. Register a handler for the new event type in the consumer
3. Implement the business logic for processing the new event type

## Monitoring and Observability

All event processing is logged with correlation IDs to enable tracing across services.
