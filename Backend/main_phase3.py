from wakeword import listen_for_wakeword
from stt_vosk import listen_and_transcribe
from llm_core import process_query

def run():
    while True:
        if not listen_for_wakeword():
            continue
        text = listen_and_transcribe()
        if not text:
            print("🤷 No command captured. Try again.")
            continue

        print(f"🧠 Query: {text}")
        reply = process_query(text)
        print(f"🤖 Sofi: {reply}")
        # stop after one round for this phase:
        break

if __name__ == "__main__":
    run()
