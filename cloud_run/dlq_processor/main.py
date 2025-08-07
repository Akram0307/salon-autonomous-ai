import json
import logging
from typing import Dict, Any
from flask import Flask, request
from google.cloud import pubsub_v1
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
ALERT_EMAIL = os.environ.get("ALERT_EMAIL", "admin@example.com")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "user@example.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "password")

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.route("/process-dlq-message", methods=["POST"])
def process_dlq_message():
    """Endpoint to process Pub/Sub DLQ messages"""
    try:
        # Get the Pub/Sub message
        envelope = request.get_json()

        # Validate the envelope
        if not envelope:
            return {"error": "No Pub/Sub message received"}, 400

        if "message" not in envelope:
            return {"error": "Invalid Pub/Sub message format"}, 400

        # Extract the message data
        message = envelope["message"]
        if "data" not in message:
            return {"error": "No data in Pub/Sub message"}, 400

        # Decode and parse the message data
        message_data = json.loads(message["data"])

        # Extract event details
        event_type = message_data.get('type')
        event_version = message_data.get('version')
        correlation_id = message_data.get('correlation_id')
        payload = message_data.get('payload', {})

        logger.warning(f"Processing DLQ message for {event_type} v{event_version} event (correlation_id: {correlation_id})")

        # Log the failed message for debugging
        log_failed_message(message_data, message.get("attributes", {}))

        # Send alert for the failed message
        send_alert(message_data, correlation_id)

        # For manual intervention, we could store the message in a database
        # or send it to another topic for manual processing
        # This is a placeholder for that functionality
        store_for_manual_intervention(message_data, correlation_id)

        logger.info(f"Successfully processed DLQ message for event {event_type} (correlation_id: {correlation_id})")

        return ("", 204)  # Return 204 No Content for successful processing

    except Exception as e:
        logger.error(f"Error processing DLQ message: {e}", exc_info=True)
        return {"error": str(e)}, 500

def log_failed_message(message_data: Dict[str, Any], attributes: Dict[str, str]):
    """Log the failed message for debugging purposes"""
    logger.error(f"Failed message details: {json.dumps(message_data, indent=2)}")
    logger.error(f"Message attributes: {json.dumps(attributes, indent=2)}")

def send_alert(message_data: Dict[str, Any], correlation_id: str):
    """Send an alert about the failed message"""
    try:
        event_type = message_data.get('type', 'Unknown')
        event_version = message_data.get('version', 'Unknown')
        tenant_id = message_data.get('tenant_id', 'Unknown')

        subject = f"ALERT: Failed Event Processing - {event_type} v{event_version}"
        body = f"""
A message has failed to process after maximum retry attempts and has been moved to the Dead Letter Queue.

Event Type: {event_type}
Event Version: {event_version}
Tenant ID: {tenant_id}
Correlation ID: {correlation_id}

Please investigate this issue as soon as possible.

Message payload:
{json.dumps(message_data, indent=2)}
        """

        # Send email alert (in a real implementation, you would use a proper email service)
        logger.info(f"Sending alert for failed message: {subject}")
        # send_email_alert(subject, body)

        # In a production environment, you might also send alerts to:
        # - Slack/Teams channels
        # - PagerDuty
        # - Cloud Monitoring alerts

    except Exception as e:
        logger.error(f"Error sending alert: {e}", exc_info=True)

def store_for_manual_intervention(message_data: Dict[str, Any], correlation_id: str):
    """Store the failed message for manual intervention"""
    # In a real implementation, you would store this in a database
    # or send it to another topic for manual processing
    logger.info(f"Storing message for manual intervention (correlation_id: {correlation_id})")

    # Example: Send to a manual intervention topic
    # publish_to_manual_intervention_topic(message_data, correlation_id)

def send_email_alert(subject: str, body: str):
    """Send an email alert (placeholder implementation)"""
    # This is a placeholder for the actual email sending logic
    # In a real implementation, you would use a proper email service
    # like SendGrid, Mailgun, or SMTP

    # Example implementation using SMTP:
    # msg = MIMEMultipart()
    # msg["From"] = SMTP_USER
    # msg["To"] = ALERT_EMAIL
    # msg["Subject"] = subject
    # msg.attach(MIMEText(body, "plain"))
    # 
    # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    # server.starttls()
    # server.login(SMTP_USER, SMTP_PASSWORD)
    # server.send_message(msg)
    # server.quit()

    pass

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
