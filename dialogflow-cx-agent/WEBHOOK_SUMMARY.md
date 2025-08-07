
# Dialogflow CX Webhook Configuration Summary

After importing the configuration files into the Dialogflow CX agent, the following steps should be taken to configure the webhooks and test the integration:

## Update Webhook URLs

1. Navigate to the Webhooks section in the Dialogflow CX Console.
2. Update the URI for each webhook to point to the corresponding core API endpoint:
   - Booking Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/bookings
   - Reschedule Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/bookings/reschedule
   - Cancel Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/bookings/cancel
   - Info Webhook: https://booking-service-salon-autonomous-ai-467811.uc.r.appspot.com/api/salon/info

3. Ensure that each webhook is configured to send requests with the correct API key in the x-api-key header.

## Test Integration

1. Use the Dialogflow CX Console to simulate user requests through the agent.
2. Verify that the webhooks are correctly calling the core API endpoints.
3. Check that bookings are being created, rescheduled, and canceled as expected.
4. Verify that salon information queries are handled correctly.

## Troubleshooting

- If webhooks are not being called, check the URI and API key configuration.
- If bookings are not being created, check the core API service logs for errors.
- If the agent is not responding as expected, review the intent training phrases and entity definitions.
