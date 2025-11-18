from vosk import Model, KaldiRecognizer
import pyaudio, json

model = Model("../models/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)
mic = pyaudio.PyAudio()

stream = mic.open(format=pyaudio.paInt16, channels=1,
                  rate=16000, input=True, frames_per_buffer=4000)
stream.start_stream()
print("🎙️ Say something...")

while True:
    data = stream.read(2000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        print("You said:", result.get("text", ""))
        break

stream.stop_stream(); stream.close(); mic.terminate()
