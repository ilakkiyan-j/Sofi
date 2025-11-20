import requests
import json
import re
from memory.context import recall
from llm.system_prompt import SYSTEM_PROMPT
from llm.tools_registry import TOOLS_SCHEMA, TOOLS
from config import OLLAMA_URL, LLM_MODEL


def process_query(user_text: str) -> str:
    # 1. Retrieve memory
    context = recall(user_text)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": f"Memory context: {context}"},
        {"role": "user", "content": user_text}
    ]

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "stream": False,
        "options": {"temperature": 0.1}  # Slightly higher temp for better speech
    }

    try:
        # --- FIRST CALL ---
        print(f"🔹 User Query: {user_text}")
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        r.raise_for_status()

        response_msg = r.json().get("message", {})
        content = response_msg.get("content", "")
        tool_calls = response_msg.get("tool_calls", [])

        # --- GHOST TOOL CATCHER ---
        if not tool_calls and ('{"name":' in content or "```json" in content):
            print("👻 Ghost tool detected...")
            try:
                match = re.search(r'\{.*"name":\s*"(.*?)".*\}', content, re.DOTALL)
                if match:
                    tool_data = json.loads(match.group(0))
                    tool_calls = [
                        {"function": {"name": tool_data.get("name"), "arguments": tool_data.get("parameters", {})}}]
            except:
                pass

        # --- EXECUTE TOOLS ---
        if tool_calls:
            print(f"⚙️ Executing {len(tool_calls)} tool(s)...")

            # We will collect ALL tool outputs into one big string
            combined_tool_outputs = ""

            for tool in tool_calls:
                func_name = tool["function"]["name"]
                func_args = tool["function"]["arguments"]

                if func_name in TOOLS:
                    print(f"   -> Running: {func_name}")
                    try:
                        result = TOOLS[func_name](**func_args)
                        combined_tool_outputs += f"\n[Output of {func_name}]:\n{str(result)}\n"
                    except Exception as e:
                        combined_tool_outputs += f"\nError running {func_name}: {e}\n"
                else:
                    combined_tool_outputs += f"\nError: Tool {func_name} not found.\n"

            # --- THE FIX: FORCE-FEED CONTEXT ---
            # Instead of relying on chat history, we start a FRESH request
            # explicitly asking it to process the data.

            force_feed_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                I have executed the request. Here is the data returned by the system:
                ----------------
                {combined_tool_outputs[:3000]} 
                ----------------

                Based on this data, answer my original request: "{user_text}".
                If I asked to summarize, summarize it. If I asked to read, say what's in it.
                Speak naturally to Ilakkiyan.
                """}
            ]

            # Send specific payload for the summary/speech generation
            payload["messages"] = force_feed_messages
            if "tools" in payload: del payload["tools"]  # No tools allowed in step 2

            r2 = requests.post(OLLAMA_URL, json=payload, timeout=60)
            r2.raise_for_status()
            final_reply = r2.json().get("message", {}).get("content", "")

            cleaned = clean_reply(final_reply)

            # Fallback only if it REALLY fails
            if not cleaned:
                return "I read the file, but I'm having trouble summarizing it right now."

            return cleaned

        else:
            return clean_reply(content)

    except Exception as e:
        print(f"🔴 Error: {e}")
        return f"System error: {e}"


def clean_reply(text):
    if not text: return ""

    # Fix Llama list bug
    if text.strip().startswith("[") and ("'" in text or '"' in text):
        try:
            cleaned = text.strip("[]")
            parts = cleaned.split(",")
            text = parts[-1].strip().strip("'").strip('"')
        except:
            pass

    # Remove prefixes
    prefixes = ["Sofi:", "Assistant:", "AI:", "Response:", "Memory context:", "System:", "Ilakkiyan:"]
    for bad in prefixes:
        if text.strip().startswith(bad):
            text = text[len(bad):].strip()

    # Remove JSON
    if text.strip().startswith("{") and text.strip().endswith("}"):
        try:
            data = json.loads(text)
            return data.get("content", "Task complete.")
        except:
            pass

    return text.strip().strip('"').strip("'")