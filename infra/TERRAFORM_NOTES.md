# Terraform Notes for booking-service (Cloud Run)

Image pinning
- Use immutable digest to avoid drift:
  image = "asia-south1-docker.pkg.dev/salon-autonomous-ai-467811/salon-repo/booking-service@sha256:41a2012031c564e8cbf1e440f7cfe42ac3f32cbbd94042da712f1b317165a1a0"

Scaling and resources (cost-optimized defaults; adjust per SLOs)
- container_concurrency = 80
- min_instances = 0
- max_instances = 10
- cpu = 1 vCPU
- memory = 512Mi

Protection
- deletion_protection = false

Module inputs (example)
- service_name             = "booking-service"
- image                    = <pinned image digest>
- allow_unauthenticated    = false (after Gateway is in place)
- env = {
    PROJECT_ID = "salon-autonomous-ai-467811"
    FIRESTORE_EMULATOR_HOST = null # unset in prod
  }

Command/args
- command = ["gunicorn"]
- args    = ["-w","2","-b","0.0.0.0:8080","main:app"]

Ingress/Port
- ingress = "all"
- port    = 8080
