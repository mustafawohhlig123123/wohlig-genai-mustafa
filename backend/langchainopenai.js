import express from "express";
import cors from "cors";
import { Server } from "socket.io";  // Import Socket.IO
import { ChatAnthropic } from "@langchain/anthropic";

const app = express();
app.use(cors());
app.use(express.json());

const apiKey = "your-api-key";  // Replace with your actual API key

const llm = new ChatAnthropic({
  model: "claude-3-5-sonnet-20240620",
  temperature: 0,
  anthropicApiKey: apiKey,
});

// Basic chat API
app.post("/api/chat", async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    // Process the prompt with the LLM (e.g., Claude)
    const response = await llm.invoke([{ role: "user", content: prompt }]);
    
    // Send the response back to the frontend
    res.json({ response });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Something went wrong" });
  }
});

// Create HTTP server and Socket.IO instance
const server = app.listen(5000, () => {
  console.log(`Server running on http://localhost:5000`);
});

// Initialize Socket.IO
const io = new Server(server);

io.on("connection", (socket) => {
  console.log("A user connected");

  // Listen for the chat message from the frontend
  socket.on("chat message", async (msg) => {
    try {
      console.log("Message received from user:", msg);

      // Process the message with LLM (e.g., Claude) and send back a response
      const response = await llm.invoke([{ role: "user", content: msg }]);
      
      // Emit the bot's response back to the frontend
      socket.emit("bot-message", response);
    } catch (error) {
      console.error("Error processing message:", error);
      socket.emit("bot-message", "Sorry, something went wrong.");
    }
  });

  socket.on("disconnect", () => {
    console.log("A user disconnected");
  });
});
