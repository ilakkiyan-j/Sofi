import sounddevice as sd
import queue
import vosk
import json
import time
from config import VOSK_MODEL_PATH

model = vosk.Model(str(VOSK_MODEL_PATH))  # your accurate model

def listen_and_transcribe(timeout=2.5):
    q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype='int16', channels=1, callback=audio_callback):

        rec = vosk.KaldiRecognizer(model, 16000)

        start = time.time()

        while True:
            if time.time() - start > timeout:
                return None

            data = q.get()

            if rec.AcceptWaveform(data):
                result = rec.Result()
                text = json.loads(result)["text"]
                if text.strip():
                    return text

            else:
                partial = json.loads(rec.PartialResult())["partial"]
                if partial.strip():
                    start = time.time()
