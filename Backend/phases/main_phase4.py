from wakeword import listen_for_wakeword
from stt_vosk import listen_and_transcribe
from llm_core import process_query
from tts_coqui import speak

def run():
    while True:
        if not listen_for_wakeword():
            continue

        user_text = listen_and_transcribe()
        if not user_text:
            print("🤷 Sofi didn’t catch that. Try again.")
            continue

        print(f"🧠 You said: {user_text}")

        reply = process_query(user_text)
        print(f"🤖 Sofi: {reply}")

        speak(reply)
        print("🎤 Spoke response. Waiting for 'Hey Sofi' again...\n")

if __name__ == "__main__":
    run()
