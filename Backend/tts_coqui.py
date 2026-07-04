import os, simpleaudio as sa
import threading
from pathlib import Path
from TTS.api import TTS
from config import COQUI_TTS_MODEL

SPEAKER = "p294" #p294
SPEED = 0.8
ENERGY = 1.05
PITCH = 1.0

os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"

tts = TTS(COQUI_TTS_MODEL, progress_bar=False, gpu=False)

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

        out_path = Path("sofi_reply.wav")
        text = text.replace(
            "Ilakkiyan",
            "<phoneme alphabet='ipa' ph='iːˈlʌk.jən'>Ilakkiyan</phoneme>"
        )
        tts.tts_to_file(
            text=text,
            file_path=str(out_path),
            speaker=SPEAKER,
            speed=SPEED,
            energy=ENERGY,
            pitch=PITCH
        )

        # 🔊 Play inline (no external app)
        wave_obj = sa.WaveObject.from_wave_file(str(out_path))
        current_play_obj = wave_obj.play()

    current_play_obj.wait_done()


