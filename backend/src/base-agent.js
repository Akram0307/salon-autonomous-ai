// Base agent class
module.exports = class BaseAgent {
  constructor(name) {
    this.name = name;
  }

  async execute(task) {
    // Common functionality for all agents
    console.log(`Executing task with ${this.name}`);
    return await this.processTask(task);
  }

  async processTask(task) {
    // To be implemented by subclasses
    throw new Error(processTask method must be implemented by subclasses);
  }
};
