// Main entry point
const orchestrator = require(./src/index);

// Start server
const express = require(express);
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.post(/agent-task, async (req, res) => {
  try {
    const result = await orchestrator.execute(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`AI Agents server running on port ${port}`);
});
