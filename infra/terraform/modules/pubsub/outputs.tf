output "topic_names" {
  description = "The names of the Pub/Sub topics."
  value       = { for k, v in google_pubsub_topic.topics : k => v.name }
}
