import os, simpleaudio as sa
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

def speak(text: str):
    text = text.strip()
    if not text:
        return

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
    play_obj = wave_obj.play()
    play_obj.wait_done()

