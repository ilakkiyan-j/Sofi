import React, { useState } from "react";
import SofiOrb from "./SofiOrb";
import Waveform from "./Waveform";
import ChatBox from "./ChatBox";
import InputBar from "./InputBar";
import "./ui.css";

export default function ChatWindowLayout({ listening, waveformActive, messages, typing, onSend })
{

    const [micActive, setMicActive] = useState(false);



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


    return (
        <div className="chat-window">

            <div className="visual-section">
                <SofiOrb listening={listening} />
                <Waveform active={micActive || waveformActive} />
            </div>

            <div className="interactions">
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
