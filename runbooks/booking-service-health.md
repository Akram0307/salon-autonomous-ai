# Booking Service Health Runbook

Canonical URL
- https://booking-service-fz7fnhwmca-el.a.run.app

Working health endpoints
- GET https://booking-service-fz7fnhwmca-el.a.run.app/health -> 200 JSON {"status":"healthy"}
- GET https://booking-service-fz7fnhwmca-el.a.run.app/_healthz -> 200 JSON {"status":"healthy"}
- GET https://booking-service-fz7fnhwmca-el.a.run.app/readyz -> 200 JSON {"status":"ready"}

Note
- GET https://booking-service-fz7fnhwmca-el.a.run.app/healthz returns 404 from Google Frontend. Use /_healthz for health checks.

Samples
- curl -i https://booking-service-fz7fnhwmca-el.a.run.app/health
- curl -i https://booking-service-fz7fnhwmca-el.a.run.app/_healthz
- curl -i https://booking-service-fz7fnhwmca-el.a.run.app/api/services

Recent logs (last 100 lines, 10m freshness)
- gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="booking-service"'   --project=salon-autonomous-ai-467811 --freshness=10m --limit=100 --format='value(textPayload)'
