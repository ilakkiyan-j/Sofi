import React, { useState, useEffect } from "react";
import ChatWindowLayout from "./components/ChatWindowLayout";

export default function App() {
    const [messages, setMessages] = useState([]);
    const [listening, setListening] = useState(false);
    const [typing, setTyping] = useState(false);
    const [waveform, setWaveform] = useState(false);

    // History states
    const [sessions, setSessions] = useState([]);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);

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

    // Fetch session list
    const fetchSessions = async () => {
        try {
            const res = await fetch("http://localhost:8000/sessions");
            const data = await res.json();
            setSessions(data);
        } catch (e) {
            console.error("Failed to load sessions:", e);
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

    // Load full details of a session
    const loadSession = async (sessionId) => {
        try {
            const res = await fetch(`http://localhost:8000/sessions/${sessionId}`);
            const data = await res.json();

            // Map backend messages format to frontend sender/text
            if (data && data.messages) {
                setMessages(data.messages.map(m => ({
                    sender: m.sender,
                    text: m.text
                })));
            } else {
                setMessages([]);
            }
            setCurrentSessionId(sessionId);
        } catch (e) {
            console.error("Failed to load session details:", e);
        }
    };

    const handleSelectSession = async (sessionId) => {
        // Stop any active speaking before loading new chat
        try {
            await fetch("http://localhost:8000/stop_speech", { method: "POST" });
        } catch (e) {
            console.error("Failed to stop speech", e);
        }
        await loadSession(sessionId);
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

    // 🔥 NEW CHAT — clear active messages, stop speech, set sessionId to null
    const handleNewChat = async () => {
        try {
            await fetch("http://localhost:8000/clear_chat", { method: "POST" });
        } catch (e) {
            console.error("Failed to clear chat", e);
        }
        setMessages([]);
        setCurrentSessionId(null);
    };

    // 🔥 PIN / UNPIN SESSION
    const handleTogglePin = async (sessionId, isPinned) => {
        try {
            await fetch(`http://localhost:8000/sessions/${sessionId}/pin`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ is_pinned: isPinned }),
            });
            fetchSessions();
        } catch (e) {
            console.error("Failed to toggle pin:", e);
        }
    };

    // 🔥 DELETE SESSION
    const handleDeleteSession = async (sessionId) => {
        try {
            await fetch(`http://localhost:8000/sessions/${sessionId}`, {
                method: "DELETE",
            });
            if (currentSessionId === sessionId) {
                setMessages([]);
                setCurrentSessionId(null);
            }
            fetchSessions();
        } catch (e) {
            console.error("Failed to delete session:", e);
        }
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
                body: JSON.stringify({
                    text,
                    mute: voiceMuted,
                    session_id: currentSessionId
                }),
            });

            const data = await res.json();

            // UI: add Sofi message
            addMessage({ sender: "sofi", text: data.response });

            // Set current session ID if it was created/returned
            if (data.session_id) {
                setCurrentSessionId(data.session_id);
            }

            // Refresh sidebar list
            fetchSessions();
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
            // History props
            sessions={sessions}
            currentSessionId={currentSessionId}
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            onSelectSession={handleSelectSession}
            onTogglePin={handleTogglePin}
            onDeleteSession={handleDeleteSession}
        />
    );
}


