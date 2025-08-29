resource "google_artifact_registry_repository" "repos" {
  for_each     = toset(var.repos)
  project      = var.project_id
  location     = var.region
  repository_id= each.key
  format       = "DOCKER"
  
  lifecycle {
    prevent_destroy = false
    ignore_changes  = [repository_id]
  }
}
