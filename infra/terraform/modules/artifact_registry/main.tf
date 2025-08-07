variable "project_id" { type=string }
variable "region" { type=string }
variable "repos" { type=list(string) }
resource "google_artifact_registry_repository" "repos" {
  for_each     = toset(var.repos)
  project      = var.project_id
  location     = var.region
  repository_id= each.key
  format       = "DOCKER"
}
