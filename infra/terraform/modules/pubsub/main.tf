variable "project_id" { type=string }
variable "topics" { type=list(string) }
resource "google_pubsub_topic" "topics" {
  for_each = toset(var.topics)
  name     = each.key
  project  = var.project_id
}
resource "google_pubsub_subscription" "subs" {
  for_each = google_pubsub_topic.topics
  name  = replace(each.key, ".", "-")
  topic = each.value.name
}
