import React from "react";
import "./ui.css";

const renderTextWithLinksAndFormatting = (text) => {
    const tokens = [];
    let lastIndex = 0;

    // Combined regex for links, bold, code, and raw urls
    const regex = /(\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]]+)\]\(((?:https?:\/\/|www\.)\S+?)\)|(?<!\()((?:https?:\/\/|www\.)[^\s\)]+?))(?=[.,;:!?]*(?:\s|$))/g;

    let match;
    while ((match = regex.exec(text)) !== null) {
        const matchIndex = match.index;

        // Add plain text before the match
        if (matchIndex > lastIndex) {
            tokens.push({ type: "text", content: text.substring(lastIndex, matchIndex) });
        }

        if (match[1].startsWith("**")) {
            tokens.push({ type: "bold", content: match[2] });
        } else if (match[1].startsWith("`")) {
            tokens.push({ type: "code", content: match[3] });
        } else if (match[4] !== undefined) {
            let url = match[5];
            if (url.startsWith("www.")) url = "https://" + url;
            tokens.push({ type: "link", content: match[4], url: url });
        } else if (match[6] !== undefined) {
            let url = match[6];
            if (url.startsWith("www.")) url = "https://" + url;
            tokens.push({ type: "link", content: match[6], url: url });
        }

        lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
        tokens.push({ type: "text", content: text.substring(lastIndex) });
    }

    return tokens.map((t, idx) => {
        switch (t.type) {
            case "bold":
                return <strong key={idx}>{t.content}</strong>;
            case "code":
                return <code key={idx}>{t.content}</code>;
            case "link":
                return (
                    <a key={idx} href={t.url} target="_blank" rel="noopener noreferrer" className="chat-link">
                        {t.content}
                    </a>
                );
            default:
                return t.content;
        }
    });
};

const parseMarkdown = (text) => {
    if (!text) return "";

    // Split text by paragraphs (double newlines)
    const paragraphs = text.split(/\n\n+/);

    return paragraphs.map((para, pIdx) => {
        const lines = para.split(/\n/);
        const renderedElements = [];
        let currentList = null; // { type: 'ul' | 'ol', items: [] }

        const flushList = (key) => {
            if (currentList) {
                const ListTag = currentList.type;
                renderedElements.push(
                    <ListTag key={key} className="chat-list">
                        {currentList.items.map((item, idx) => (
                            <li key={idx}>{renderTextWithLinksAndFormatting(item)}</li>
                        ))}
                    </ListTag>
                );
                currentList = null;
            }
        };

        lines.forEach((line, lIdx) => {
            const trimmed = line.trim();
            const bulletMatch = trimmed.match(/^[\*\-]\s+(.*)$/);
            const numberMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);

            if (bulletMatch) {
                if (currentList && currentList.type !== "ul") {
                    flushList(`list-transition-${lIdx}`);
                }
                if (!currentList) {
                    currentList = { type: "ul", items: [] };
                }
                currentList.items.push(bulletMatch[1]);
            } else if (numberMatch) {
                if (currentList && currentList.type !== "ol") {
                    flushList(`list-transition-${lIdx}`);
                }
                if (!currentList) {
                    currentList = { type: "ol", items: [] };
                }
                currentList.items.push(numberMatch[2]);
            } else {
                flushList(`list-flush-${lIdx}`);
                if (trimmed) {
                    renderedElements.push(
                        <p key={`p-${lIdx}`} className="chat-paragraph">
                            {renderTextWithLinksAndFormatting(line)}
                        </p>
                    );
                }
            }
        });

        flushList(`list-final-${lines.length}`);

        return (
            <div key={pIdx} className="chat-para-block">
                {renderedElements}
            </div>
        );
    });
};

export default function ChatBox({ messages, typing }) {
    return (
        <div className="chatbox">
            {messages.map((msg, i) => (
                <div key={i} className={`msg ${msg.sender}`}>
                    {parseMarkdown(msg.text)}
                </div>
            ))}

            {typing && (
                <div className="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            )}
        </div>
    );
}
