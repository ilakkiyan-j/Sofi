import React from "react";
import "./ui.css";

export default function Waveform({ active }) {
    return (
        <div className={`waveform-container ${active ? "active" : ""}`}>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
        </div>
    );
}
