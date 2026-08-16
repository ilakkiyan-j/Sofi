import numpy as np
import io
import time
import asyncio
from typing import Optional, Tuple
from config import MODELS_DIR
from tools.logger import log
from events import event_bus, EVENT_VOICE_INTERRUPT, EVENT_STT_PARTIAL, EVENT_STT_FINAL

FASTER_WHISPER_AVAILABLE = False
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False


class FasterWhisperSTT:
    """
    Sub-second Streaming Speech-To-Text Engine using CTranslate2 int8 quantized Whisper.
    Features real-time Voice Activity Detection (VAD) and barge-in interruption.
    """
    def __init__(self, model_size: str = "tiny.en", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None
        self.is_speaking = False
        self.last_speech_time = time.time()
        self.silence_threshold = 0.003

        self.load_model()

    def load_model(self):
        if FASTER_WHISPER_AVAILABLE:
            try:
                log(f"🎙️ Loading Faster-Whisper ({self.model_size}, {self.compute_type}) on {self.device}...")
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=str(MODELS_DIR / "whisper")
                )
                log("✅ Faster-Whisper STT Engine loaded successfully!")
            except Exception as e:
                log(f"⚠️ Faster-Whisper load error: {e}")
                self.model = None
        else:
            log("ℹ️ Faster-Whisper not installed. Falling back to Vosk STT.")

    def transcribe_audio_ndarray(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcribes a 1D float32 numpy array of audio PCM samples.
        """
        if not self.model:
            return ""

        try:
            # Ensure float32 format normalized to [-1.0, 1.0]
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32) / 32768.0

            segments, _ = self.model.transcribe(
                audio_data,
                beam_size=1,
                best_of=1,
                temperature=0.0,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            text_parts = [segment.text for segment in segments]
            return " ".join(text_parts).strip()
        except Exception as e:
            log(f"🔴 Faster-Whisper transcription error: {e}")
            return ""

    def process_voice_chunk(self, chunk_pcm: bytes, is_tts_speaking: bool = False) -> Tuple[bool, float]:
        """
        Processes a raw 20ms PCM micro-chunk. Detects speech volume level for barge-in.
        If user speaks while TTS is active, triggers instant EVENT_VOICE_INTERRUPT!
        """
        audio_array = np.frombuffer(chunk_pcm, dtype=np.int16).astype(np.float32) / 32768.0
        volume = float(np.abs(audio_array).mean()) if len(audio_array) > 0 else 0.0

        has_speech = volume > self.silence_threshold

        if has_speech:
            self.last_speech_time = time.time()
            if is_tts_speaking:
                log("⚡ Barge-In Triggered by STT VAD Volume!")
                asyncio.create_task(event_bus.publish(EVENT_VOICE_INTERRUPT, {"source": "vad_barge_in"}))

        return has_speech, volume


# Global singleton instance
whisper_stt_engine = FasterWhisperSTT()
