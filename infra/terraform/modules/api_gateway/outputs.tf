output "gateway_url" {
  value = google_api_gateway_gateway.api.default_hostname
}
