import React, { useState } from "react";
import ChatWindowLayout from "./components/ChatWindowLayout";

export default function App() {
    const [messages, setMessages] = useState([]);
    const [listening, setListening] = useState(false);
    const [typing, setTyping] = useState(false);
    const [waveform, setWaveform] = useState(false);
    const [voiceMuted, setVoiceMuted] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem("sofi_voice_muted") || "false");
        } catch {
            return false;
        }
    });

    const addMessage = (msg) => {
        setMessages((prev) => [...prev, msg]);
    };

    // 🔥 TOGGLE MUTE
    const handleToggleMute = async () => {
        const newMute = !voiceMuted;
        setVoiceMuted(newMute);
        localStorage.setItem("sofi_voice_muted", JSON.stringify(newMute));

        if (newMute) {
            try {
                await fetch("http://localhost:8000/stop_speech", { method: "POST" });
            } catch (e) {
                console.error("Failed to stop active speech", e);
            }
        }
    };

    // 🔥 NEW CHAT — clear messages + backend memory
    const handleNewChat = async () => {
        try {
            await fetch("http://localhost:8000/clear_chat", { method: "POST" });
        } catch (e) {
            console.error("Failed to clear chat", e);
        }
        setMessages([]);
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
                body: JSON.stringify({ text, mute: voiceMuted }),
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
            voiceMuted={voiceMuted}
            onToggleMute={handleToggleMute}
            onNewChat={handleNewChat}
        />
    );
}

