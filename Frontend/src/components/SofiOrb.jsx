import React from "react";
import "./ui.css";

export default function SofiOrb({ listening }) {
    return (
        <div className={`sofi-orb ${listening ? "listening" : ""}`}>
            <div className="orb-liquid"></div>
            <div className="orb-glow"></div>
        </div>
    );
}
