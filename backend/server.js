require("dotenv").config();
const express = require("express");
const cors = require("cors");
const connectDB = require("./config/db");
const predictRoutes = require("./routes/predict");

const app = express();

// Connect to MongoDB
connectDB();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/api", predictRoutes);

// Base route
app.get("/", (req, res) => {
  res.send("MERN Backend is Running!");
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
