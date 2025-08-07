variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region where the Cloud Run service will be deployed."
  type        = string
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
}

variable "image" {
  description = "The Docker image URL for the Cloud Run service."
  type        = string
}

variable "allow_unauthenticated" {
  description = "Whether to allow unauthenticated access to the service."
  type        = bool
  default     = false
}

variable "env" {
  description = "Environment variables for the Cloud Run service."
  type        = map(string)
  default     = {}
}

variable "max_instances" {
  description = "Maximum number of instances for the Cloud Run service."
  type        = number
  default     = 100
}
