// Orchestration agent
const BaseAgent = require(./base-agent);

class OrchestratorAgent extends BaseAgent {
  constructor() {
    super(OrchestratorAgent);
    this.agents = {};
  }

  registerAgent(agent) {
    this.agents[agent.name] = agent;
  }

  async processTask(task) {
    // Route task to appropriate agent
    const agent = this.agents[task.agent];
    if (agent) {
      return await agent.execute(task);
    } else {
      throw new Error(`Agent ${task.agent} not found`);
    }
  }
}

module.exports = OrchestratorAgent;
