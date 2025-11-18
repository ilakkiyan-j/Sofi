import chromadb, os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

client = chromadb.Client()
memory = client.get_or_create_collection("sofi_memory")

# Store some data
memory.add(
    documents=["Ilakkiyan loves building AI assistants."],
    ids=["1"],
    metadatas=[{"topic": "AI"}]
)

# Query
query = "Who likes building AI?"
result = memory.query(query_texts=[query], n_results=1)

print("🧠 Query:", query)
print("📄 Match:", result['documents'][0][0])
print("💬 Distance:", result['distances'][0][0])
