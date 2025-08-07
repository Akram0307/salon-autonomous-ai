output "booking_created_topic_name" {
  description = "The name of the booking created Pub/Sub topic."
  value       = google_pubsub_topic.booking_created.name
}

output "booking_updated_topic_name" {
  description = "The name of the booking updated Pub/Sub topic."
  value       = google_pubsub_topic.booking_updated.name
}

output "booking_cancelled_topic_name" {
  description = "The name of the booking cancelled Pub/Sub topic."
  value       = google_pubsub_topic.booking_cancelled.name
}
