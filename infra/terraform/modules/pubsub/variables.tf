# This file defines variables for the pubsub module

variable "project_id" {
  type        = string
  description = "The ID of the Google Cloud project"
}

variable "topics" {
  type        = list(string)
  description = "List of Pub/Sub topic names to create"
}
