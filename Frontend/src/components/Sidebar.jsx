import React, { useState } from "react";
import {
    RiPushpin2Fill,
    RiPushpin2Line,
    RiDeleteBin6Line,
    RiSearchLine,
    RiMessage3Line,
    RiAddLine,
    RiCloseLine
} from "react-icons/ri";
import "./ui.css";

export default function Sidebar({
    isOpen,
    onClose,
    sessions,
    currentSessionId,
    onSelectSession,
    onTogglePin,
    onDeleteSession,
    onNewChat
}) {
    const [searchQuery, setSearchQuery] = useState("");

    const filteredSessions = sessions.filter((s) =>
        s.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const pinnedSessions = filteredSessions.filter((s) => s.is_pinned);
    const recentSessions = filteredSessions.filter((s) => !s.is_pinned);

    return (
        <div className={`history-sidebar ${isOpen ? "open" : ""}`}>
            <div className="sidebar-header">
                <h3>Chat History</h3>
                <button className="close-sidebar-btn" onClick={onClose} title="Close History">
                    <RiCloseLine size={20} />
                </button>
            </div>

            <button className="sidebar-new-chat-btn" onClick={onNewChat} title="New Chat">
                <RiAddLine size={20} />
                <span>New Chat</span>
            </button>

            <div className="sidebar-search-box">
                <RiSearchLine className="search-icon" size={18} />
                <input
                    type="text"
                    placeholder="Search chats..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searchQuery && (
                    <button className="clear-search-btn" onClick={() => setSearchQuery("")}>
                        &times;
                    </button>
                )}
            </div>

            <div className="sidebar-list-container">
                {pinnedSessions.length > 0 && (
                    <div className="sidebar-group">
                        <div className="group-title">Pinned</div>
                        {pinnedSessions.map((s) => (
                            <SessionItem
                                key={s.id}
                                session={s}
                                isActive={s.id === currentSessionId}
                                onSelect={onSelectSession}
                                onTogglePin={onTogglePin}
                                onDelete={onDeleteSession}
                            />
                        ))}
                    </div>
                )}

                <div className="sidebar-group">
                    <div className="group-title">{pinnedSessions.length > 0 ? "Recent" : "Chats"}</div>
                    {recentSessions.length > 0 ? (
                        recentSessions.map((s) => (
                            <SessionItem
                                key={s.id}
                                session={s}
                                isActive={s.id === currentSessionId}
                                onSelect={onSelectSession}
                                onTogglePin={onTogglePin}
                                onDelete={onDeleteSession}
                            />
                        ))
                    ) : (
                        filteredSessions.length === 0 && (
                            <div className="no-chats-placeholder">No chats found</div>
                        )
                    )}
                </div>
            </div>
        </div>
    );
}

function SessionItem({ session, isActive, onSelect, onTogglePin, onDelete }) {
    const handleItemClick = (e) => {
        // Prevent trigger if clicking action buttons
        if (e.target.closest(".item-action-btn")) return;
        onSelect(session.id);
    };

    const handleDeleteClick = (e) => {
        e.stopPropagation();
        const confirmDelete = window.confirm(`Delete chat "${session.title}"?`);
        if (confirmDelete) {
            onDelete(session.id);
        }
    };

    return (
        <div
            className={`session-item ${isActive ? "active" : ""}`}
            onClick={handleItemClick}
            title={session.title}
        >
            <RiMessage3Line className="session-icon" size={16} />
            <span className="session-title">{session.title}</span>

            <div className="session-item-actions">
                <button
                    className="item-action-btn pin-btn"
                    onClick={(e) => {
                        e.stopPropagation();
                        onTogglePin(session.id, !session.is_pinned);
                    }}
                    title={session.is_pinned ? "Unpin Chat" : "Pin Chat"}
                >
                    {session.is_pinned ? (
                        <RiPushpin2Fill size={16} className="pinned-active" />
                    ) : (
                        <RiPushpin2Line size={16} />
                    )}
                </button>
                <button
                    className="item-action-btn delete-btn"
                    onClick={handleDeleteClick}
                    title="Delete Chat"
                >
                    <RiDeleteBin6Line size={16} />
                </button>
            </div>
        </div>
    );
}
