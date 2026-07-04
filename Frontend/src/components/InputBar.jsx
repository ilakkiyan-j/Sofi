import React, { useState } from "react";
import { RiMicFill } from "react-icons/ri";
import "./ui.css";

export default function InputBar({ onSend, onMicToggle, micActive }) {
    const [text, setText] = useState("");

    const send = () => {
        if (!text.trim()) return;
        onSend(text);
        setText("");
    };

    return (
        <div className="input-bar">
            <button
                className={`mic-button ${micActive ? "active" : ""}`}
                onClick={onMicToggle}
                title={micActive ? "Stop Listening" : "Start Listening"}
            >
                <RiMicFill size={22} />
            </button>

            <input
                value={text}
                placeholder="Type a message..."
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
            />

            <button className="send-btn" onClick={send}>➤</button>
        </div>
    );
}


