import os
import json
import time
import uuid
import threading

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "chat_sessions.json")
sessions_lock = threading.Lock()

def _load_raw_sessions():
    """Load session database with thread safety."""
    if not os.path.exists(SESSIONS_FILE):
        return {"sessions": []}
    
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading sessions: {e}")
        return {"sessions": []}

def _save_raw_sessions(data):
    """Save session database with thread safety."""
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving sessions: {e}")

def get_sessions_list():
    """Retrieve metadata of all sessions sorted by pin status and update time."""
    with sessions_lock:
        db = _load_raw_sessions()
        result = []
        for s in db.get("sessions", []):
            result.append({
                "id": s["id"],
                "title": s["title"],
                "created_at": s.get("created_at", 0),
                "updated_at": s.get("updated_at", 0),
                "is_pinned": s.get("is_pinned", False)
            })
        # Sort: Pinned first, then by updated_at descending
        result.sort(key=lambda x: (x["is_pinned"], x["updated_at"]), reverse=True)
        return result

def get_session_details(session_id: str):
    """Retrieve full details of a specific session."""
    with sessions_lock:
        db = _load_raw_sessions()
        for s in db.get("sessions", []):
            if s["id"] == session_id:
                return s
        return None

def create_session(first_message_text: str):
    """Create a new session, auto-generating a title from the first message."""
    with sessions_lock:
        db = _load_raw_sessions()
        
        # Clean title: strip first 35 chars
        title = first_message_text.strip()
        if len(title) > 35:
            title = title[:32] + "..."
        if not title:
            title = "New Chat"

        now = int(time.time())
        new_session = {
            "id": f"session_{int(now)}_{uuid.uuid4().hex[:6]}",
            "title": title,
            "created_at": now,
            "updated_at": now,
            "is_pinned": False,
            "messages": []
        }
        
        db["sessions"].append(new_session)
        _save_raw_sessions(db)
        return new_session

def add_message_to_session(session_id: str, sender: str, text: str):
    """Append a message to a session, updating its timestamp."""
    with sessions_lock:
        db = _load_raw_sessions()
        found = False
        target_session = None
        
        for s in db.get("sessions", []):
            if s["id"] == session_id:
                s["messages"].append({
                    "sender": sender,
                    "text": text,
                    "timestamp": int(time.time())
                })
                s["updated_at"] = int(time.time())
                target_session = s
                found = True
                break
        
        if found:
            _save_raw_sessions(db)
        return target_session

def toggle_pin_session(session_id: str, is_pinned: bool):
    """Set the pinned state of a session."""
    with sessions_lock:
        db = _load_raw_sessions()
        updated = False
        for s in db.get("sessions", []):
            if s["id"] == session_id:
                s["is_pinned"] = is_pinned
                updated = True
                break
        
        if updated:
            _save_raw_sessions(db)
        return updated

def delete_session(session_id: str):
    """Delete a session from history."""
    with sessions_lock:
        db = _load_raw_sessions()
        sessions = db.get("sessions", [])
        new_sessions = [s for s in sessions if s["id"] != session_id]
        
        if len(new_sessions) != len(sessions):
            db["sessions"] = new_sessions
            _save_raw_sessions(db)
            return True
        return False
