output "url" {
  description = "The URL of the Cloud Run service."
  value       = google_cloud_run_v2_service.svc.uri
}

output "service_account_email" {
  description = "The email of the service account created for the Cloud Run service."
  value       = google_service_account.run_sa.email
}
