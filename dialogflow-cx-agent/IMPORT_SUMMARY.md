
# Dialogflow CX Agent Import Summary

The following configuration files have been processed and are ready to be imported into the Dialogflow CX agent:

## Intents
- booking_service.json
- cancel_booking.json
- reschedule_booking.json
- salon_information.json

## Entities
- customer_name.json
- date.json
- phone_number.json
- service_type.json
- time.json

## Webhooks
- booking_webhook.json
- cancel_webhook.json
- info_webhook.json
- reschedule_webhook.json

## Flows
- main.json

To import these files into the Dialogflow CX agent:

1. Create a new Dialogflow CX agent in the Google Cloud Console.
2. Obtain the AGENT_ID from the agent's settings.
3. Update the processed JSON files in the temp directory with the actual AGENT_ID and API_KEY.
4. Use the Dialogflow CX Console or API to import each configuration file:
   - Import intents
   - Import entities
   - Import webhooks
   - Import flows

After importing, proceed to configure the webhooks and test the integration.
