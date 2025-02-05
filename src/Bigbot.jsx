import React, { useState } from "react";
import "./Chatbot.css";

const Bigbot = () => {
  const [userInput, setUserInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (userInput.trim() !== "") {
      const newMessage = { sender: "user", text: userInput };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      
      try {
        const response = await fetch("http://localhost:5000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: userInput }),
        });

        const data = await response.json();
        const botMessage = { sender: "bot", text: data.response || "Sorry, something went wrong." };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } catch (error) {
        console.error("Error communicating with chatbot API:", error);
      }

      setUserInput("");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">Chatbot</div>
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

export default Bigbot;