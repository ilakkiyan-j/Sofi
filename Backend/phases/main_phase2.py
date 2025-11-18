from wakeword import listen_for_wakeword
from stt_vosk import listen_and_transcribe

def run():
    while True:
        woke = listen_for_wakeword()
        if not woke:
            continue
        cmd = listen_and_transcribe()
        if not cmd:
            print("🤷 No speech detected. Say “Hey Sofi” again.")
            continue
        print(f"✅ Phase-2 OK. Command captured: {cmd}")
        # For this phase we stop after one interaction:
        break

if __name__ == "__main__":
    run()
