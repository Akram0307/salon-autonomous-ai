output "api_gateway_url" {
  value = module.api_gateway.gateway_url
}

output "cloud_run_urls" {
  value = module.run_services.service_urls
}
