import json
import re
import httpx
import asyncio
from typing import AsyncGenerator, Dict, Any
from memory.context import recall
from llm.system_prompt import SYSTEM_PROMPT
from llm.tools_registry import TOOLS_SCHEMA, TOOLS
from llm.core import should_enable_tools, clean_reply
from config import OLLAMA_URL, LLM_MODEL
from tools.logger import log


async def async_process_query_stream(user_text: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Asynchronous streaming generator for Ollama LLM requests.
    Yields dictionary event packets:
    - {"type": "token", "content": str}
    - {"type": "tool_start", "name": str, "arguments": dict}
    - {"type": "tool_finish", "name": str, "result": Any}
    - {"type": "done", "full_text": str}
    """
    # 1. Retrieve memory context (non-blocking thread execution)
    context = await asyncio.to_thread(recall, user_text)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Recalled memories about the user:\n{context}" if context else "No relevant memories recalled."},
        {"role": "user", "content": user_text}
    ]

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.1}
    }

    if should_enable_tools(user_text):
        payload["tools"] = TOOLS_SCHEMA

    accumulated_content = ""
    tool_calls = []
    first_token_sent = False

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            log(f"🔹 Async Streaming Query: {user_text}")
            async with client.stream("POST", OLLAMA_URL, json=payload) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg = chunk.get("message", {})
                    token = msg.get("content", "")
                    
                    if token:
                        accumulated_content += token
                        if not first_token_sent:
                            first_token_sent = True
                            yield {"type": "first_token_latency"}
                        
                        yield {"type": "token", "content": token}

                    if "tool_calls" in msg and msg["tool_calls"]:
                        tool_calls.extend(msg["tool_calls"])

            # Ghost tool check if no explicit tool call returned by Ollama JSON API
            if not tool_calls and ('{"name":' in accumulated_content or "```json" in accumulated_content):
                log("👻 Ghost tool detected in stream...")
                try:
                    match = re.search(r'\{.*"name":\s*"(.*?)".*\}', accumulated_content, re.DOTALL)
                    if match:
                        tool_data = json.loads(match.group(0))
                        tool_calls = [
                            {"function": {"name": tool_data.get("name"), "arguments": tool_data.get("parameters", {})}}
                        ]
                except Exception as e:
                    log(f"Ghost tool parsing error: {e}")

            # If tool calls were requested by LLM
            if tool_calls:
                log(f"⚙️ Executing {len(tool_calls)} streaming tool(s)...")
                combined_tool_outputs = ""

                for tool in tool_calls:
                    func_name = tool.get("function", {}).get("name")
                    func_args = tool.get("function", {}).get("arguments", {})

                    yield {
                        "type": "tool_start",
                        "name": func_name,
                        "arguments": func_args
                    }

                    if func_name in TOOLS:
                        log(f"   -> Running Tool: {func_name}")
                        try:
                            # Run synchronous tool functions safely off the main event loop thread
                            result = await asyncio.to_thread(TOOLS[func_name], **func_args)
                            result_str = str(result)
                            combined_tool_outputs += f"\n[Output of {func_name}]:\n{result_str}\n"
                            yield {
                                "type": "tool_finish",
                                "name": func_name,
                                "result": result_str,
                                "status": "success"
                            }
                        except Exception as err:
                            err_msg = f"Error executing {func_name}: {err}"
                            combined_tool_outputs += f"\n{err_msg}\n"
                            yield {
                                "type": "tool_finish",
                                "name": func_name,
                                "result": err_msg,
                                "status": "error"
                            }
                    else:
                        not_found = f"Error: Tool {func_name} not found."
                        combined_tool_outputs += f"\n{not_found}\n"
                        yield {
                            "type": "tool_finish",
                            "name": func_name,
                            "result": not_found,
                            "status": "error"
                        }

                # Send tool output back to Ollama with streaming enabled
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

                tool_summary_payload = {
                    "model": LLM_MODEL,
                    "messages": force_feed_messages,
                    "stream": True,
                    "options": {"temperature": 0.1}
                }

                accumulated_tool_reply = ""
                async with client.stream("POST", OLLAMA_URL, json=tool_summary_payload) as summary_response:
                    summary_response.raise_for_status()

                    async for line in summary_response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                accumulated_tool_reply += token
                                yield {"type": "token", "content": token}
                        except json.JSONDecodeError:
                            continue

                final_cleaned = clean_reply(accumulated_tool_reply)
                yield {"type": "done", "full_text": final_cleaned}

            else:
                final_cleaned = clean_reply(accumulated_content)
                yield {"type": "done", "full_text": final_cleaned}

        except Exception as e:
            log(f"🔴 Async LLM Stream Error: {e}")
            yield {"type": "error", "error": str(e)}
            yield {"type": "done", "full_text": f"System error: {e}"}
