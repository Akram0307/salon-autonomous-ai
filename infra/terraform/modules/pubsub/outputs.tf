output "topic_names" {
  description = "The names of the Pub/Sub topics."
  value       = { for k, v in google_pubsub_topic.topics : k => v.name }
}

output "dlq_topic_names" {
  description = "The names of the DLQ Pub/Sub topics."
  value       = { for k, v in google_pubsub_topic.dlq_topics : k => v.name }
}

output "subscription_names" {
  description = "The names of the Pub/Sub subscriptions."
  value       = { for k, v in google_pubsub_subscription.subs : k => v.name }
}
