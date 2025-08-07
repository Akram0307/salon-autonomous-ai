terraform {
  backend "gcs" {
    bucket = "salon-autonomous-ai-467811-tfstate"
    prefix = "terraform/state"
  }
}
