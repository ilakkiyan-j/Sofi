import React from "react";
import "./ui.css";

export default function ChatBox({ messages, typing }) {
    return (
        <div className="chatbox">
            {messages.map((msg, i) => (
                <div key={i} className={`msg ${msg.sender}`}>
                    <p>{msg.text}</p>
                </div>
            ))}

            {typing && (
                <div className="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            )}
        </div>
    );
}
