import React, { useState } from "react";
import SofiOrb from "./SofiOrb";
import Waveform from "./Waveform";
import ChatBox from "./ChatBox";
import InputBar from "./InputBar";
import Sidebar from "./Sidebar";
import {
    RiExpandDiagonalLine,
    RiContractLeftLine,
    RiVolumeUpFill,
    RiVolumeMuteFill,
    RiRefreshLine,
    RiHistoryLine
} from "react-icons/ri";
import "./ui.css";

export default function ChatWindowLayout({
    listening,
    waveformActive,
    messages,
    typing,
    onSend,
    voiceMuted,
    onToggleMute,
    onNewChat,
    sessions,
    currentSessionId,
    sidebarOpen,
    setSidebarOpen,
    onSelectSession,
    onTogglePin,
    onDeleteSession
}) {
    const [micActive, setMicActive] = useState(false);
    const [expanded, setExpanded] = useState(false);

    const handleMicToggle = () => {
        setMicActive(prev => {
            const newState = !prev;

            if (newState) {
                // MIC ON
                fetch("http://127.0.0.1:8000/start_listening", { method: "POST" });
            } else {
                // MIC OFF
                fetch("http://127.0.0.1:8000/stop_listening", { method: "POST" })
                    .then(res => res.json())
                    .then(data => {
                        if (data.text && data.text.trim() !== "") {
                            onSend(data.text);
                        }
                    });
            }

            return newState;
        });
    };

    const handleExpand = () => {
        setExpanded(prev => !prev);
    };

    const handleRefreshClick = () => {
        const confirmClear = window.confirm("Are you sure you want to clear the chat and start a new session?");
        if (confirmClear) {
            onNewChat();
        }
    };

    return (
        <div className={`chat-window ${expanded ? "expanded" : ""} ${sidebarOpen ? "sidebar-visible" : ""}`}>
            <Sidebar
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
                sessions={sessions}
                currentSessionId={currentSessionId}
                onSelectSession={(sid) => {
                    onSelectSession(sid);
                    // On small screens/normal size, auto-close sidebar on select
                    if (!expanded) setSidebarOpen(false);
                }}
                onTogglePin={onTogglePin}
                onDeleteSession={onDeleteSession}
                onNewChat={onNewChat}
            />

            <div className="top-left-actions">
                <button
                    className={`icon-button history-btn ${sidebarOpen ? "active" : ""}`}
                    onClick={() => setSidebarOpen(prev => !prev)}
                    title="Toggle Chat History"
                >
                    <RiHistoryLine size={22} />
                </button>
                <button
                    className="icon-button expand-btn"
                    onClick={handleExpand}
                    title={expanded ? "Collapse Window" : "Expand Window"}
                >
                    {expanded ? <RiContractLeftLine size={22} /> : <RiExpandDiagonalLine size={22} />}
                </button>
                <button
                    className="icon-button refresh-btn"
                    onClick={handleRefreshClick}
                    title="New Chat"
                >
                    <RiRefreshLine size={22} />
                </button>
            </div>

            <div className={`visual-section ${expanded ? "expanded" : ""}`}>
                <SofiOrb listening={listening} expanded={expanded} />

                <button
                    className={`mute-button ${voiceMuted ? "muted" : ""}`}
                    onClick={onToggleMute}
                    title={voiceMuted ? "Unmute Sofi Voice" : "Mute Sofi Voice"}
                >
                    {voiceMuted ? <RiVolumeMuteFill size={22} /> : <RiVolumeUpFill size={22} />}
                </button>

                <Waveform active={micActive || waveformActive} />
            </div>

            <div className={`interactions ${expanded ? "expanded" : ""}`}>
                <ChatBox messages={messages} typing={typing} />

                <InputBar
                    onSend={onSend}
                    onMicToggle={handleMicToggle}
                    micActive={micActive}
                />
            </div>

        </div>
    );
}
