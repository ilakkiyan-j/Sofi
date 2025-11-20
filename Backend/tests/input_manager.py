import threading
import queue
import time

from stt_vosk import listen_and_transcribe
from logger import log, silent_mode

input_queue = queue.Queue()

SILENCE_TIMEOUT = 2.5  # 2.5 seconds

def audio_listener():
    while True:
        spoken = listen_and_transcribe(timeout=SILENCE_TIMEOUT)

        if not spoken:
            continue

        bad = ["the", "the.", "a", "uh", "huh", "mmm", "mm", "ah"]
        if spoken.lower().strip() in bad:
            continue

        input_queue.put(("audio", spoken))


def text_listener():
    global silent_mode

    while True:
        silent_mode = True
        typed = input("").strip()
        silent_mode = False

        if typed:
            input_queue.put(("text", typed))
