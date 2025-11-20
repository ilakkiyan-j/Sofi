from wakeword import listen_for_wakeword
from llm_core import process_query
from tts_coqui import speak
from memory import remember

from input_manager import audio_listener, text_listener, input_queue
import threading


def run():
    print("Sofi is idle... say 'Hey Sofi' to wake her up.")

    # Start background listeners
    threading.Thread(target=audio_listener, daemon=True).start()
    threading.Thread(target=text_listener, daemon=True).start()

    while True:

        if not listen_for_wakeword():
            continue

        print("🟢 Wake word detected!")
        speak("Yes? I am listening.")
        print("🟢 Sofi is awake! Speak or type now. Say 'stop' to exit.")

        while True:
            print("🎧 Waiting for input (voice or text)...")

            source, user_text = input_queue.get()  # waits for ANY input

            print(f"🧠 ({source}) You said: {user_text}")

            # STOP conversation
            if user_text.lower() in ["stop", "bye"]:
                speak("Okay, stopping now.")
                print("⛔ Conversation ended. Say 'Hey Sofi' again.")
                break

            # LLM response
            reply = process_query(user_text)
            print(f"🤖 Sofi: {reply}")

            remember(user_text, reply)
            speak(reply)


if __name__ == "__main__":
    run()
