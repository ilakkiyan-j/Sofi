import chromadb
import os
from sentence_transformers import SentenceTransformer

os.environ["ANONYMIZED_TELEMETRY"] = "False"

client = chromadb.Client()
collection = client.get_or_create_collection("sofi_memory")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# In-session short-term memory
conversation_state = {
    "last_user_intent": None,
    "last_tool_used": None,
    "last_params": None
}


# What should be stored as long-term memory?
def is_meaningful_memory(user_text, reply):
    user_text = user_text.lower()

    # Don't save trivial chat
    trivial = ["hi", "hello", "hey", "thanks", "ok", "hmm"]
    if user_text.strip() in trivial:
        return False

    # Don't save repeated confirmations
    if "again" in user_text or "repeat" in user_text:
        return False

    # Don't save tool outputs, results, or "ok done" style replies
    if len(reply) < 5:
        return False

    # Good memories: preferences, personal details, long sentences
    if len(user_text.split()) >= 4:
        return True

    return False


def remember(user_text: str, reply: str):
    """Store meaningful long-term memory."""
    if not is_meaningful_memory(user_text, reply):
        return

    uid = str(abs(hash(user_text)))[-12:]
    collection.add(
        documents=[f"User said: {user_text}\nSofi replied: {reply}"],
        ids=[uid]
    )
    print("💾 Long-term memory saved.")


def recall(query: str, top_k=3) -> str:
    """Retrieve relevant memory."""
    try:
        results = collection.query(query_texts=[query], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs)
    except:
        return ""


# Conversation memory handlers
def set_last_action(tool_name, params):
    conversation_state["last_tool_used"] = tool_name
    conversation_state["last_params"] = params


def get_last_action():
    return conversation_state.get("last_tool_used"), conversation_state.get("last_params")
