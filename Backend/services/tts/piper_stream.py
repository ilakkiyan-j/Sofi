import os
import sys
import asyncio
import threading
import queue
import wave
import io
from pathlib import Path
from io import BytesIO
from typing import Generator, Optional
from config import BACKEND_ROOT, MODELS_DIR
from tools.logger import log
from events import event_bus, EVENT_VOICE_INTERRUPT, EVENT_TTS_CHUNK

# Try importing piper
PIPER_AVAILABLE = False
try:
    from piper import PiperVoice, AudioChunk
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False


class StreamingTTSEngine:
    """
    Sub-second ONNX Streaming TTS Engine.
    Synthesizes sentence chunks into raw PCM audio bytes and pushes them
    over WebSocket / Audio queues with immediate interruption (barge-in) support.
    """
    def __init__(self, model_path: Optional[Path] = None):
        self.voice = None
        self.model_path = model_path or (MODELS_DIR / "en_US-lessac-medium.onnx")
        self.is_interrupted = False
        self.active_playback_lock = threading.Lock()
        self._playback_thread = None
        self.audio_queue = queue.Queue()

        # Subscribe to interruption events
        event_bus.subscribe(EVENT_VOICE_INTERRUPT, self.handle_interrupt)

        self.load_model()

    def load_model(self):
        if PIPER_AVAILABLE and self.model_path.exists():
            try:
                log(f"🔊 Loading Piper ONNX Voice model from {self.model_path}")
                self.voice = PiperVoice.load(str(self.model_path))
                log("✅ Piper ONNX TTS Engine loaded successfully!")
            except Exception as e:
                log(f"⚠️ Failed to load Piper ONNX model: {e}")
                self.voice = None
        else:
            log("ℹ️ Piper ONNX model not present or piper not installed. Coqui/System fallback active.")

    async def handle_interrupt(self, event):
        """Immediately stop current TTS synthesis and playback upon user voice barge-in."""
        log("⚡ Voice Barge-In: Interrupting active speech playback!")
        self.is_interrupted = True
        self.clear_audio_queue()

    def clear_audio_queue(self):
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()

    def synthesize_sentence_pcm(self, text: str) -> Generator[bytes, None, None]:
        """
        Synthesizes a single sentence string into raw 16-bit 22.05kHz PCM audio bytes.
        """
        if self.is_interrupted:
            return

        text = text.strip()
        if not text:
            return

        if self.voice and PIPER_AVAILABLE:
            try:
                # PiperVoice.synthesize yields AudioChunk objects
                for chunk in self.voice.synthesize(text):
                    if self.is_interrupted:
                        break
                    if hasattr(chunk, 'audio_bytes'):
                        yield chunk.audio_bytes
                    elif isinstance(chunk, bytes):
                        yield chunk
            except Exception as e:
                log(f"Piper ONNX synthesis error: {e}")
        else:
            # Fallback mock/Coqui audio synthesis indicator
    def speak_text(self, text: str):
        if self.is_interrupted:
            return
        text = text.strip()
        if not text:
            return

        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            log(f"🔊 Playing Voice Audio: {text[:50]}...")
            speaker.Speak(text)
        except Exception as e:
            log(f"🔊 TTS Output: {text} ({e})")

    def interrupt(self):
        self.is_interrupted = True
        self.clear_audio_queue()

    def reset_interruption(self):
        self.is_interrupted = False


# Global Streaming TTS instance
tts_engine = StreamingTTSEngine()
