import os

os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"

from TTS.api import TTS

tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
tts.tts_to_file(
    text="Hello Lucifer!, I am Sofi speaking naturally now.",
    file_path="sofi_voice.wav",
    speaker="p294",
    speed=0.9,
    energy=1.05,
    pitch=1.02
)

print("✅ Sofi’s natural voice generated: sofi_voice.wav")
