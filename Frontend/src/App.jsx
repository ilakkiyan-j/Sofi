import React, { useState } from "react";
import ChatWindowLayout from "./components/ChatWindowLayout";

export default function App() {
    const [messages, setMessages] = useState([]);
    const [listening, setListening] = useState(false);
    const [typing, setTyping] = useState(false);
    const [waveform, setWaveform] = useState(false);

    const addMessage = (msg) => {
        setMessages((prev) => [...prev, msg]);
    };

    // 🔥 SEND TEXT TO BACKEND
    const handleSend = async (text) => {
        // UI: show user message
        addMessage({ sender: "user", text });

        // UI: show typing indicator
        setTyping(true);

        try {
            const res = await fetch("http://localhost:8000/send_text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });

            const data = await res.json();

            // UI: add Sofi message
            addMessage({ sender: "sofi", text: data.response });
        } catch (e) {
            addMessage({ sender: "sofi", text: "(Backend error, try again)" });
        }

        setTyping(false);
    };

    return (
        <ChatWindowLayout
            listening={listening}
            waveformActive={waveform}
            messages={messages}
            typing={typing}
            onSend={handleSend}
        />
    );
}
