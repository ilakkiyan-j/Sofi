import chromadb, os
from sentence_transformers import SentenceTransformer

os.environ["ANONYMIZED_TELEMETRY"] = "False"

client = chromadb.Client()
collection = client.get_or_create_collection("sofi_memory")

# embedder used for semantic similarity
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def remember(user_text: str, reply: str):
    """Store a user–assistant pair in memory."""
    uid = str(hash(user_text))[-10:]
    collection.add(documents=[f"User: {user_text}\nSofi: {reply}"], ids=[uid])
    print("💾 Memory saved.")

def recall(query: str, top_k=2) -> str:
    """Retrieve most relevant past context."""
    results = collection.query(query_texts=[query], n_results=top_k)
    docs = results.get("documents", [[]])[0]
    return "\n".join(docs)
