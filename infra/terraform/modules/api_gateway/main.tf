resource "google_api_gateway_api" "api" {
  provider = google-beta
  api_id   = var.api_name
  project  = var.project_id
  
}

resource "google_api_gateway_api_config" "api" {
  provider      = google-beta
  api           = google_api_gateway_api.api.api_id
  api_config_id = "${var.api_name}-config"
  project       = var.project_id
  
  openapi_documents {
    document {
      path     = "openapi.yaml"
      contents = base64encode(templatefile(var.openapi_spec_path, {
        firebase_jwt_issuer   = var.firebase_jwt_issuer
        firebase_jwt_audience = var.firebase_jwt_audience
        backends              = var.backends
      }))
    }
  }
}

resource "google_api_gateway_gateway" "api" {
  provider   = google-beta
  api_config = google_api_gateway_api_config.api.id
  gateway_id = var.gateway_id
  project    = var.project_id
  region     = var.region
}
