import sounddevice as sd
import queue, json, time
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH
from tools.logger import log

model = Model(str(VOSK_MODEL_PATH))
samplerate = 16000

q = queue.Queue()
stream = None
recording = False

# More sensitive for Indian accent
SILENCE_THRESHOLD = 0.002
SILENCE_DURATION = 1.0
MIN_LISTEN_TIME = 0.6


def audio_callback(indata, frames, time_info, status):
    if recording:
        q.put(indata.copy())


def start_listening_stream():
    global stream, recording

    if stream:
        try:
            stream.stop()
            stream.close()
        except:
            pass

    q.queue.clear()
    recording = True

    log("🎙️  Listening started")

    stream = sd.InputStream(
        channels=1,
        samplerate=samplerate,
        dtype="int16",
        blocksize=1024,
        callback=audio_callback
    )
    stream.start()


def stop_and_transcribe():
    global stream, recording

    recording = False

    if stream:
        stream.stop()
        stream.close()
        log("🔕  Listening ended")

    rec = KaldiRecognizer(model, samplerate)
    audio_started = False
    last_sound_time = time.time()
    start_time = time.time()

    while True:
        try:
            data = q.get(timeout=0.1)
        except:
            if audio_started and \
               (time.time() - last_sound_time) > SILENCE_DURATION and \
               (time.time() - start_time) > MIN_LISTEN_TIME:
                break
            continue

        # Volume detection
        volume = abs(float(data.mean()))
        if volume > SILENCE_THRESHOLD:
            audio_started = True
            last_sound_time = time.time()

        rec.AcceptWaveform(data.tobytes())

    result = json.loads(rec.FinalResult()).get("text", "")
    log(f"📝 Recognized: {result}")

    return result

