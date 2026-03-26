const mongoose = require("mongoose");

const logSchema = mongoose.Schema({
  user_id: { type: String, required: true },
  date: { type: Date, default: Date.now },
  sequence: { type: Array, required: true },
  prediction_score: { type: Number, required: true },
  risk_message: { type: String, required: true },
  explanation: { type: String }
});

const Log = mongoose.model("Log", logSchema);

module.exports = Log;
