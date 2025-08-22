const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Basic health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'Salon Management API is running' });
});

// Salon endpoints
app.get('/api/salons', (req, res) => {
  res.json({ message: 'Get all salons endpoint' });
});

app.post('/api/salons', (req, res) => {
  res.json({ message: 'Create salon endpoint' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
