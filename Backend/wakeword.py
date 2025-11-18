import struct, pyaudio, pvporcupine
from config import ACCESS_KEY, WAKEWORD_PPN, SENSITIVITY

def listen_for_wakeword():
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[str(WAKEWORD_PPN)],
        sensitivities=[SENSITIVITY],
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate, channels=1,
        format=pyaudio.paInt16, input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("🎧 Sofi idle… say: “Hey Sofi”")
    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            if porcupine.process(pcm) >= 0:
                print("🟢 Wake word detected!")
                return True
    finally:
        stream.stop_stream(); stream.close(); pa.terminate(); porcupine.delete()
