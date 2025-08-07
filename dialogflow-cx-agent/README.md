# Dialogflow CX Agent for Salon Management System

This directory contains the configuration files for the Dialogflow CX agent used in the salon management system.

## Structure

- `intents/`: Contains JSON files for each intent (booking service, reschedule booking, cancel booking, salon information)
- `entities/`: Contains JSON files for each entity (service type, date, time, customer name, phone number)
- `webhooks/`: Contains JSON files for each webhook (booking, reschedule, cancel, info)
- `flows/`: Contains JSON files for each flow (main flow)
- `temp/`: Directory for processed configuration files (created during deployment)
- `deploy.sh`: Deployment script to process configuration files and replace placeholders
- `IMPORT_SUMMARY.md`: Summary of steps to import configuration files into Dialogflow CX agent
- `WEBHOOK_SUMMARY.md`: Summary of steps to configure webhooks and test integration

## Deployment

1. Set the GOOGLE_CLOUD_PROJECT_ID environment variable to your project ID (e.g., 'salon-autonomous-ai-467811').
2. Update the deploy.sh script in the dialogflow-cx-agent directory with the correct PROJECT_ID and LOCATION_ID (e.g., asia-south1).
3. Run the deploy.sh script to process the configuration files and replace placeholders. This creates processed JSON files in the temp directory.
4. Create a new Dialogflow CX agent in the Google Cloud Console to obtain the AGENT_ID.
5. Update the processed JSON files in the temp directory with the actual AGENT_ID and API_KEY for the booking service.
6. Import the processed configuration files (intents, entities, webhooks, flows) from the temp directory into your Dialogflow CX agent using the Dialogflow CX API or Console.
7. Update the webhook URLs in the Dialogflow CX agent to point to the core API endpoints (e.g., https://booking-service-PROJECT_ID.uc.r.appspot.com/api/bookings).
8. Ensure the webhooks are configured to send requests with the correct API key in the x-api-key header.
9. Test the integration by simulating user requests through the Dialogflow CX agent.
10. Verify that the webhooks are correctly calling the core API endpoints and that bookings are being created.

## Integration with Core API

The Dialogflow CX agent is integrated with the core API endpoints for booking management. The webhooks are configured to call the following endpoints:

- Booking Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/bookings
- Reschedule Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/bookings/reschedule
- Cancel Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/bookings/cancel
- Info Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/salon/info

## Troubleshooting

- If webhooks are not being called, check the URI and API key configuration.
- If bookings are not being created, check the core API service logs for errors.
- If the agent is not responding as expected, review the intent training phrases and entity definitions.
