variable "project_id" { type=string }
variable "region" { type=string }

resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com","firestore.googleapis.com","pubsub.googleapis.com","cloudbuild.googleapis.com","artifactregistry.googleapis.com","apigateway.googleapis.com","secretmanager.googleapis.com","workflows.googleapis.com","cloudscheduler.googleapis.com","cloudtasks.googleapis.com","monitoring.googleapis.com","logging.googleapis.com","aiplatform.googleapis.com","bigquery.googleapis.com"
  ])
  project = var.project_id
  service = each.key
}

resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}
