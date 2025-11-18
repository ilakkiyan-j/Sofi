from pathlib import Path
import pvporcupine, pyaudio, struct

ACCESS_KEY = "0ooE6IdBMmlxbVBAVnUUnu5elZO1MBk01nkGzJ42tfxFbcsrSxKOxA=="  # your key

# Build absolute path relative to this file
ROOT = Path(__file__).resolve().parents[1]           # → ...\Backend
KEYWORD_PATH = ROOT / "wakeword" / "hey-sofi.ppn"

# Sanity check
if not KEYWORD_PATH.exists():
    raise FileNotFoundError(f"Wakeword file not found at: {KEYWORD_PATH}")

porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keyword_paths=[str(KEYWORD_PATH)],  # cast to str for the lib
    sensitivities=[0.6],
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate, channels=1,
    format=pyaudio.paInt16, input=True,
    frames_per_buffer=porcupine.frame_length,
)

print(f"🎧 Listening, keyword: {KEYWORD_PATH.name}")
while True:
    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    if porcupine.process(pcm) >= 0:
        print("🟢 Wake word detected!")
        break

stream.stop_stream(); stream.close(); pa.terminate(); porcupine.delete()
