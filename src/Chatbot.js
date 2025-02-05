import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import "./Chatbot.css";
import { useRef } from "react";

const Chatbot = () => {
  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState([]);
  const socket = useRef(null); // useRef to persist the socket connection

  useEffect(() => {
    socket.current = io("http://localhost:5000"); // Connect only once

    socket.current.on("bot-message", (message) => {
      setMessages((prevMessages) => [...prevMessages, { sender: "bot", text: message }]);
    });

    return () => {
      socket.current.disconnect(); // Cleanup socket connection when the component unmounts
    };
  }, []); // Empty dependency array ensures this runs only once

  const sendMessage = () => {
    if (userInput.trim() !== "") {
      setMessages((prevMessages) => [...prevMessages, { sender: "user", text: userInput }]);
      socket.current.emit("chat message", userInput); // Use socket from useRef
      setUserInput("");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        Chatbot
      </div>
      <div className="message-area">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}-message`}>
            <div className="text">{msg.text}</div>
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message"
          className="input-field"
        />
        <button onClick={sendMessage} className="send-button">Send</button>
      </div>
    </div>
  );
};

export default Chatbot;
