const express = require("express");
const cors = require("cors");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const http = require("http");
const socketIo = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3005",  // Allow frontend URL
    methods: ["GET", "POST"],        // Allow necessary HTTP methods
  },
});

// Middleware
app.use(cors({
  origin: "http://localhost:3005",   // Allow frontend URL
  methods: ["GET", "POST"],
  allowedHeaders: ["Content-Type"],
}));
app.use(express.json()); // Make sure this is included to parse JSON bodies

// Initialize the GoogleGenerativeAI instance with your API key
const genAI = new GoogleGenerativeAI(""); // Replace with your actual API key

// Get the Gemini model (gemini-1.5-flash)
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

// Store past conversations
let conversationHistory = [];

// API Endpoint to accept user input and return Gemini response via WebSocket
app.post("/api/chat", async (req, res) => {
  try {
    // Make sure the request body has a 'prompt' property
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    // Add the current user's message to the conversation history
    conversationHistory.push({ sender: "user", text: prompt });

    let finalPrompt = `You are a robot. Please give me an answer in points, and prefix every point with an arrow. The starting words for each point should be in bold to act as a main header. Your task is to respond to the following question while remembering the context of the conversation. The conversation history is as follows:\n`;

    conversationHistory.forEach((message) => {
      finalPrompt += `${message.sender}: ${message.text}\n`;
    });

    finalPrompt += `Your prompt is: ${prompt}`;

    // Generate content using the Gemini model based on the user's prompt
    const result = await model.generateContent(finalPrompt);

    // Simulate streaming by sending the response in parts
    const fullResponse = result.response.text();
    let index = 0;

    // Emit the response incrementally to the frontend
    const sendStream = () => {
      if (index < fullResponse.length) {
        const nextChar = fullResponse[index++];
        io.emit('bot-message', nextChar); // Emit each character to the frontend
        setTimeout(sendStream, 50); // Delay before sending the next character
      } else {
        io.emit('bot-message', ''); // Emit empty string when done (indicating end of message)
      }
    };

    sendStream(); // Start sending the response in chunks

    res.status(200).send({ status: 'Message sent to the frontend' });

  } catch (error) {
    console.error("Error with Gemini API:", error);
    res.status(500).json({ error: error.message });
  }
});

// Start the server
const PORT = 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
//hi
