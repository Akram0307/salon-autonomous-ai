variable "project_id" { type=string }
variable "topics" { type=list(string) }

# Create regular topics
resource "google_pubsub_topic" "topics" {
  for_each = toset(var.topics)
  name     = each.key
  project  = var.project_id
}

# Create DLQ topics
resource "google_pubsub_topic" "dlq_topics" {
  for_each = toset(var.topics)
  name     = "${each.key}-dlq"
  project  = var.project_id
}

# Create subscriptions with dead letter policies
resource "google_pubsub_subscription" "subs" {
  for_each = google_pubsub_topic.topics
  name  = replace(each.key, ".", "-")
  topic = each.value.name

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dlq_topics[each.key].id
    max_delivery_attempts = 5
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}
