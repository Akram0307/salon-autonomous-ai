// Main entry point
const OrchestratorAgent = require(./src/orchestrator);
const ConversationalBookingAgent = require(./src/conversational-booking-agent);
const DynamicPricingAgent = require(./src/dynamic-pricing-agent);
const LTVForecastingAgent = require(./src/ltv-forecasting-agent);
const StaffProductivityAgent = require(./src/staff-productivity-agent);
const SafetyComplianceAgent = require(./src/safety-compliance-agent);

// Initialize orchestrator
const orchestrator = new OrchestratorAgent();

// Register agents
orchestrator.registerAgent(new ConversationalBookingAgent());
orchestrator.registerAgent(new DynamicPricingAgent());
orchestrator.registerAgent(new LTVForecastingAgent());
orchestrator.registerAgent(new StaffProductivityAgent());
orchestrator.registerAgent(new SafetyComplianceAgent());

// Export orchestrator
module.exports = orchestrator;
