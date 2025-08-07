# Salon AI Agents

This directory contains the implementation of 21 AI agents for the salon management system.

## Agent Categories

1. **Core Customer & Booking Agents**:
   - Conversational Booking Agent
   - Stylist Assignment Agent
   - Appointment Modification Agent
   - Service Recommendation Agent

2. **Revenue & Marketing Agents**:
   - Dynamic Pricing Agent
   - Personalized Offers Agent
   - Ad Campaign Agent
   - Upsell/Cross-sell Agent

3. **Customer Retention Agents**:
   - LTV Forecasting Agent
   - Churn Risk Agent
   - Loyalty Program Agent
   - Review Request Agent

4. **Operational Agents**:
   - Staff Productivity Agent
   - Inventory Management Agent
   - Financial Reconciliation Agent
   - Waitlist Management Agent

5. **System Management Agents**:
   - Orchestration Agent
   - Safety & Compliance Agent
   - Data Quality Agent
   - Performance Monitoring Agent
   - Error Handling Agent

## Implementation Details

- Base agent class for common functionality
- Orchestration agent to coordinate all agents
- Implementation using Vertex AI's Gemini models via Node.js SDK
- Proper error handling and task routing

## Dependencies

- express: ^4.18.2
- @google-cloud/vertexai: ^1.1.0

## Usage

To start the AI agents server:

```bash
npm start
```

The server will listen on port 3000 by default.
