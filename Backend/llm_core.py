import requests
from memory import recall

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3"

SYSTEM_PROMPT = """
You are Sofi — an offline voice-based AI assistant created by Ilakkiyan J.

🎙️ OUTPUT RULES (VERY IMPORTANT):
- Speak ONLY the reply. 
- NEVER prefix with “Sofi:”, “Assistant:”, “User:”, or any labels.
- NEVER describe yourself speaking (no “Sofi says” or “I respond by saying”).
- NEVER write explanations or narration.
- Your output must be ONLY the sentence Sofi would say aloud.

🧠 Personality:
- Warm, human-like, friendly, slightly witty.
- Short, natural answers (1–2 sentences unless asked for more).

📘 Memory Rules:
- When user says “my name is X”, remember it.
- If user asks “who am I”, use the remembered name.
- Use memory naturally without mentioning “memory”, “database”, etc.

🚫 Avoid:
- No references to AI, models, instructions, or being offline.
- No role-play formatting.
- No disclaimers.
"""

def process_query(user_text: str) -> str:
    # Retrieve relevant memory
    context = recall(user_text)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": f"Memory context: {context}"},
            {"role": "user", "content": user_text}
        ],
        "stream": False
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        r.raise_for_status()

        data = r.json()
        reply = (data.get("message", {}).get("content", "")).strip()

        # Remove unwanted prefixes Llama sometimes adds
        for bad in ["Sofi:", "Assistant:", "assistant:", "AI:", "Response:"]:
            if reply.startswith(bad):
                reply = reply[len(bad):].strip()

        return reply.strip() if reply else "(Sofi didn't respond.)"

    except Exception as e:
        return f"(LLM error: {e})"
