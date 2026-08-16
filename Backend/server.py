import os
import sys

def _patch_add_dll_directory():
    if getattr(sys, 'frozen', False):
        _orig_add_dll_directory = os.add_dll_directory
        def _add_dll_directory(*args, **kwargs):
            try:
                return _orig_add_dll_directory(*args, **kwargs)
            except FileNotFoundError:
                pass
        os.add_dll_directory = _add_dll_directory

_patch_add_dll_directory()

# Hotfix PyInstaller TorchScript JIT getsourcelines OSError (Can't get source for fused_add_tanh_sigmoid_multiply)
if getattr(sys, 'frozen', False):
    import torch
    def script_method(fn, _rcb=None):
        return fn
    def script(obj, optimize=True, _frames_up=0, _rcb=None):
        return obj
    torch.jit.script = script
    torch.jit.script_method = script_method

    # Hotfix PyInstaller typeguard inspect UnicodeDecodeError
    import typeguard
    def dummy_typechecked(*args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return args[0]
        return lambda fn: fn
    typeguard.typechecked = dummy_typechecked

import json
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from stt_vosk_server import start_listening_stream, stop_and_transcribe
from llm.core import process_query
from llm.async_core import async_process_query_stream
from events import event_bus, EVENT_LLM_TOKEN, EVENT_LLM_FIRST_TOKEN, EVENT_TOOL_START, EVENT_TOOL_FINISH
from tts_coqui import speak, stop_speak
from memory.context import remember, clear_memory
from memory.sessions import (
    get_sessions_list,
    get_session_details,
    create_session,
    add_message_to_session,
    toggle_pin_session,
    delete_session
)
from services.plugins.loader import plugin_loader
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Discover and load dynamic extensions
plugin_loader.discover_and_load_plugins()

# Allow your Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

# 🔴 MICROPHONE STREAM STATE
is_listening = False


@app.post("/start_listening")
async def start_listening():
    global is_listening
    if not is_listening:
        is_listening = True
        start_listening_stream()
    return {"status": "listening_started"}


@app.post("/stop_listening")
async def stop_listening():
    global is_listening
    if is_listening:
        is_listening = False
        text = stop_and_transcribe()
        return {"status": "done", "text": text}
    return {"status": "not_listening", "text": ""}


@app.post("/send_text")
async def handle_text(payload: dict, background_tasks: BackgroundTasks):
    text = payload.get("text", "")
    mute = payload.get("mute", False)
    session_id = payload.get("session_id", None)

    if not text:
        return {"response": "", "session_id": session_id}

    # Create session if it does not exist
    if not session_id:
        session = create_session(text)
        session_id = session["id"]

    # Save User message
    add_message_to_session(session_id, "user", text)

    # Process LLM
    reply = process_query(text)

    # Save Sofi message
    add_message_to_session(session_id, "sofi", reply)

    # Store memory context
    remember(text, reply)

    # TTS
    if not mute:
        background_tasks.add_task(speak, reply)

    return {"response": reply, "session_id": session_id}


@app.post("/send_text_stream")
async def handle_text_stream(payload: dict, background_tasks: BackgroundTasks):
    """
    HTTP Server-Sent Events (SSE) streaming endpoint.
    Yields real-time token events: data: {"type": "token", "content": "..."}\n\n
    """
    text = payload.get("text", "")
    mute = payload.get("mute", False)
    session_id = payload.get("session_id", None)

    if not text:
        async def empty_gen():
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'full_text': ''})}\n\n"
        return StreamingResponse(empty_gen(), media_type="text/event-stream")

    if not session_id:
        session = create_session(text)
        session_id = session["id"]

    add_message_to_session(session_id, "user", text)

    async def sse_generator():
        full_response = ""
        async for packet in async_process_query_stream(text):
            if packet["type"] == "token":
                full_response += packet["content"]
                await event_bus.publish(EVENT_LLM_TOKEN, {"token": packet["content"]})
            elif packet["type"] == "tool_start":
                await event_bus.publish(EVENT_TOOL_START, packet)
            elif packet["type"] == "tool_finish":
                await event_bus.publish(EVENT_TOOL_FINISH, packet)
            elif packet["type"] == "done":
                full_text = packet.get("full_text", full_response)
                add_message_to_session(session_id, "sofi", full_text)
                remember(text, full_text)
                if not mute and full_text:
                    background_tasks.add_task(speak, full_text)
                packet["session_id"] = session_id
            
            yield f"data: {json.dumps(packet)}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """
    Full-duplex WebSocket streaming endpoint for low-latency voice & text interactions.
    """
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue

            action = data.get("action", "send_text")
            if action == "send_text":
                text = data.get("text", "")
                mute = data.get("mute", False)
                session_id = data.get("session_id", None)

                if not text:
                    await websocket.send_json({"type": "done", "session_id": session_id, "full_text": ""})
                    continue

                if not session_id:
                    session = create_session(text)
                    session_id = session["id"]
                    await websocket.send_json({"type": "session_created", "session_id": session_id})

                add_message_to_session(session_id, "user", text)

                full_response = ""
                async for packet in async_process_query_stream(text):
                    if packet["type"] == "token":
                        full_response += packet["content"]
                        await event_bus.publish(EVENT_LLM_TOKEN, {"token": packet["content"]})
                    elif packet["type"] == "tool_start":
                        await event_bus.publish(EVENT_TOOL_START, packet)
                    elif packet["type"] == "tool_finish":
                        await event_bus.publish(EVENT_TOOL_FINISH, packet)
                    elif packet["type"] == "done":
                        full_text = packet.get("full_text", full_response)
                        add_message_to_session(session_id, "sofi", full_text)
                        remember(text, full_text)
                        if not mute and full_text:
                            asyncio.create_task(asyncio.to_thread(speak, full_text))
                        packet["session_id"] = session_id

                    await websocket.send_json(packet)

            elif action == "stop_speech":
                stop_speak()
                await websocket.send_json({"type": "speech_stopped"})
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        pass


@app.post("/stop_speech")
async def stop_speech():
    stop_speak()
    return {"status": "speech_stopped"}


@app.post("/clear_chat")
async def clear_chat():
    """Reset the session: stop any speech and clear long-term memory."""
    stop_speak()
    clear_memory()
    return {"status": "chat_cleared"}


@app.get("/sessions")
async def list_sessions():
    return get_sessions_list()


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = get_session_details(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/sessions/{session_id}/pin")
async def pin_session(session_id: str, payload: dict):
    is_pinned = payload.get("is_pinned", False)
    success = toggle_pin_session(session_id, is_pinned)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}


@app.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
