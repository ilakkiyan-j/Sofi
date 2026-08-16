import os, simpleaudio as sa
import threading
from pathlib import Path
from tools.logger import log

COQUI_AVAILABLE = False
tts = None

try:
    from TTS.api import TTS
    from config import COQUI_TTS_MODEL
    os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
    os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
    tts = TTS(COQUI_TTS_MODEL, progress_bar=False, gpu=False)
    COQUI_AVAILABLE = True
except Exception as e:
    log(f"ℹ️ Coqui-TTS fallback mode active ({e}). Using Piper ONNX Streaming TTS.")
    COQUI_AVAILABLE = False

# Lock and track active playback
tts_lock = threading.Lock()
current_play_obj = None

def stop_speak():
    global current_play_obj
    if current_play_obj and current_play_obj.is_playing():
        try:
            current_play_obj.stop()
        except Exception:
            pass

def speak(text: str):
    global current_play_obj
    text = text.strip()
    if not text:
        return

    with tts_lock:
        stop_speak()

        if COQUI_AVAILABLE and tts:
            try:
                out_path = Path("sofi_reply.wav")
                text_formatted = text.replace(
                    "Ilakkiyan",
                    "<phoneme alphabet='ipa' ph='iːˈlʌk.jən'>Ilakkiyan</phoneme>"
                )
                tts.tts_to_file(
                    text=text_formatted,
                    file_path=str(out_path),
                    speaker="p294",
                    speed=0.8,
                    energy=1.05,
                    pitch=1.0
                )
                wave_obj = sa.WaveObject.from_wave_file(str(out_path))
                current_play_obj = wave_obj.play()
                current_play_obj.wait_done()
                return
            except Exception as e:
                log(f"Coqui synthesis error: {e}")

        # Fallback to Windows SAPI offline voice engine
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            log(f"🔊 Playing SAPI Voice Speech: {text[:50]}...")
            speaker.Speak(text)
        except Exception as err:
            log(f"🔊 TTS Log: {text} ({err})")


