from fastapi import FastAPI
from stt_vosk_server import start_listening_stream, stop_and_transcribe
from llm_core import process_query
from tts_coqui import speak
from memory import remember
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
async def handle_text(payload: dict):
    text = payload.get("text", "")

    if not text:
        return {"response": ""}

    # Process LLM
    reply = process_query(text)

    # Store memory
    remember(text, reply)

    # TTS
    speak(reply)

    return {"response": reply}
