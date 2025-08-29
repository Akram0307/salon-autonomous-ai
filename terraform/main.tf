terraform {
  backend "gcs" {
    bucket = "salon-app-tf-state-467811"
    prefix = "terraform/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.50.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = "us-central1"
}



resource "google_storage_bucket" "tf_state" {
  name          = var.tf_state_bucket
  location      = "US"
  force_destroy = false
  versioning {
    enabled = true
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_firestore_database" "default" {
  project     = var.gcp_project_id
  name        = "(default)"
  location_id = "nam5"
  type        = "FIRESTORE_NATIVE"
}

resource "google_pubsub_topic" "salon_events" {
  name    = "salon-events"
  project = var.gcp_project_id
}
