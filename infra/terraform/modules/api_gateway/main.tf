variable "project_id" { type=string }
variable "region" { type=string }
variable "gateway_id" { type=string }
variable "openapi_spec_path" { type=string }
variable "firebase_jwt_issuer" { type=string }
variable "firebase_jwt_audience" { type=string }
variable "backends" { type=map(string) }

data "google_project" "proj" {}
locals {
  spec = templatefile(var.openapi_spec_path, {
    core-api-url = var.backends["core-api"]
  })
}
resource "google_api_gateway_api" "api" { api_id = var.gateway_id project = var.project_id }
resource "google_api_gateway_api_config" "cfg" {
  api           = google_api_gateway_api.api.name
  api_config_id = "v1"
  openapi_documents { document { path = "openapi.yaml" contents = base64encode(local.spec) } }
}
resource "google_api_gateway_gateway" "gw" {
  project    = var.project_id
  location   = var.region
  gateway_id = var.gateway_id
  api_config = google_api_gateway_api_config.cfg.id
}
output "gateway_url" { value = google_api_gateway_gateway.gw.default_hostname }
