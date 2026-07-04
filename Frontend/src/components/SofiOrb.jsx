import React from "react";
import "./ui.css";

export default function SofiOrb({ listening, expanded }) {
    return (
        <div className={`sofi-orb ${listening ? "listening" : ""} ${expanded ? "expanded" : ""}`}>
            <div className="orb-liquid"></div>
            <div className="orb-glow"></div>
            {expanded && <div className="orb-burst"></div>}
        </div>
    );
}
