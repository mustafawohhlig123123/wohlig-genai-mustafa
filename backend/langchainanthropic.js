import express from "express";
import cors from "cors";
import { Server } from "socket.io";
import { ChatAnthropic } from "@langchain/anthropic";


const app = express();


// CORS configuration for allowing frontend (localhost:3002) to connect
app.use(
 cors({
   origin: "http://localhost:3002",
   methods: ["GET", "POST"],
   allowedHeaders: ["Content-Type"],
 })
);


app.use(express.json());


const apiKey =
 "";


const llm = new ChatAnthropic({
 model: "claude-3-5-sonnet-20240620",
 temperature: 0,
 anthropicApiKey: apiKey,
});


app.post("/chat", async (req, res) => {
 try {
   const { prompt } = req.body;
   console.log("Received prompt:", prompt);
   if (!prompt) {
     return res.status(400).json({ error: "Prompt is required" });
   }


   const response = await llm.invoke([{ role: "user", content: prompt }]);
   console.log("Response from LLM:", response);
   res.json({ response });
 } catch (error) {
   console.error("Error:", error);
   res.status(500).json({ error: "Something went wrong" });
 }
});


// Create HTTP server and Socket.IO instance with CORS options
const server = app.listen(5000, () => {
 console.log(`Server running on http://localhost:5000`);
});


// Initialize Socket.IO with CORS configuration
const io = new Server(server, {
 cors: {
   origin: "http://localhost:3002",
   methods: ["GET", "POST"],
 },
});


io.on("connection", (socket) => {
 console.log("A user connected");


 // Listen for chat messages from the frontend
 socket.on("chat message", async (msg) => {
   try {
     console.log("Message received from user:", msg);
     // Process the message with LLM (e.g., Claude)
     const response = await llm.invoke([{ role: "user", content: msg }]);
     console.log("LLM response:", response);


     // Ensure only the content is sent back
     const botMessage = response?.content || "Sorry, something went wrong.";
     console.log("Emitting response to frontend:", botMessage);
     socket.emit("bot-message", botMessage);
   } catch (error) {
     console.error("Error processing message:", error);
     socket.emit("bot-message", "Sorry, something went wrong.");
   }
 });


 socket.on("disconnect", () => {
   console.log("A user disconnected");
 });
});



