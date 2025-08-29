variable "gcp_project_id" {
  description = "The GCP project ID to deploy resources into."
  type        = string
}

variable "gcp_region" {
  description = "The primary GCP region for deployment."
  type        = string
  default     = "us-central1"
}

variable "tf_state_bucket" {
  description = "The globally unique name of the GCS bucket for Terraform state."
  type        = string
}
