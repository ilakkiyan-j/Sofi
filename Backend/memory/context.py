import os
import re

os.environ["ANONYMIZED_TELEMETRY"] = "False"

# In-session short-term memory
conversation_state = {
    "last_user_intent": None,
    "last_tool_used": None,
    "last_params": None
}

# ---- Patterns that signal a personal fact the user WANTS Sofi to remember ----
PERSONAL_FACT_PATTERNS = [
    r"\bmy name is\b",
    r"\bcall me\b",
    r"\bi am\b.*(years old|yr old|engineer|developer|student|doctor)",
    r"\bi work (at|for|in)\b",
    r"\bi live in\b",
    r"\bi('m| am) from\b",
    r"\bremember that\b",
    r"\bdon'?t forget\b",
    r"\bkeep in mind\b",
    r"\bi prefer\b",
    r"\bi like\b",
    r"\bi love\b",
    r"\bi hate\b",
    r"\bi always\b",
    r"\bi never\b",
    r"\bmy favourite\b",
    r"\bmy favorite\b",
    r"\bmy (email|phone|number|address|birthday|dob)\b",
    r"\bsofi, (remember|note|save)\b",
]

def is_personal_fact(user_text: str) -> bool:
    """Return True only when the user is explicitly sharing a personal fact."""
    text = user_text.lower()
    for pattern in PERSONAL_FACT_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


from services.memory.working import working_memory
from services.memory.vector_rag import rag_engine

def remember(user_text: str, reply: str):
    """Store messages in L1 Working Memory and explicit facts in L3 Vector RAG."""
    working_memory.add_message("user", user_text)
    working_memory.add_message("sofi", reply)

    if is_personal_fact(user_text):
        rag_engine.add_memory(user_text, reply)


def recall(query: str, top_k=3) -> str:
    """Retrieve combined context from L1 Working Memory and L3 Vector RAG."""
    working_context = working_memory.format_context_prompt()
    rag_context = rag_engine.query_memories(query, top_k=top_k)

    combined = []
    if working_context:
        combined.append(f"Recent Conversation:\n{working_context}")
    if rag_context:
        combined.append(f"Recalled Long-Term Facts:\n{rag_context}")

    return "\n\n".join(combined)


def clear_memory():
    """Wipe all stored memories (used on new-chat reset)."""
    global collection
    try:
        client.delete_collection("sofi_memory")
        collection = client.get_or_create_collection("sofi_memory")
        print("🗑️ Memory cleared.")
    except Exception as e:
        print(f"Memory clear error: {e}")


# Conversation memory handlers
def set_last_action(tool_name, params):
    conversation_state["last_tool_used"] = tool_name
    conversation_state["last_params"] = params


def get_last_action():
    return conversation_state.get("last_tool_used"), conversation_state.get("last_params")

