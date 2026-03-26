const express = require("express");
const axios = require("axios");
const Log = require("../models/Log");
const router = express.Router();

router.post("/predict", async (req, res) => {
  try {
    const { user_id, sequence } = req.body;
    
    // 1. Send data to Python API to get the prediction
    const pythonResponse = await axios.post(`${process.env.PYTHON_API_URL}/predict`, {
      user_id: user_id || "user_123",
      sequence: sequence
    });

    const { risk_score, message, explanation } = pythonResponse.data;

    // 2. Save the result to MongoDB
    const newLog = new Log({
      user_id: user_id || "user_123",
      sequence: sequence,
      prediction_score: risk_score,
      risk_message: message,
      explanation: explanation
    });

    await newLog.save();

    // 3. Return the response back to React
    res.json({
      risk_score,
      message,
      explanation
    });

  } catch (error) {
    console.error("Prediction Error:", error.message);
    res.status(500).json({ error: "Failed to process prediction request." });
  }
});

router.get("/history/:user_id", async (req, res) => {
  try {
    const logs = await Log.find({ user_id: req.params.user_id })
      .sort({ date: -1 })
      .select('-_id -__v'); // Exclude mongoose internal fields

    res.json({ history: logs });
  } catch (error) {
    console.error("History Error:", error.message);
    res.status(500).json({ error: "Failed to fetch user history." });
  }
});

module.exports = router;
