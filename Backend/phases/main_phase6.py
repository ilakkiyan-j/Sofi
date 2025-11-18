from wakeword import listen_for_wakeword
from llm_core import process_query
from tts_coqui import speak
from memory import remember

from input_manager import audio_listener, text_listener, input_queue
from logger import log
import threading

def run():
    log("Sofi is idle... say 'Hey Sofi' to wake her up.")

    # background input threads
    threading.Thread(target=audio_listener, daemon=True).start()
    threading.Thread(target=text_listener, daemon=True).start()

    while True:

        if not listen_for_wakeword():
            continue

        log("🟢 Wake word detected!")
        speak("Yes? I am listening.")
        log("🟢 Sofi is awake! Speak or type. Say 'stop' to exit.")

        while True:
            log("🎧 Waiting for input (voice or text)...")

            source, user_text = input_queue.get()

            log(f"🧠 ({source}) You said: {user_text}")

            if user_text.lower() in ["stop", "bye"]:
                speak("Okay, stopping now.")
                log("⛔ Conversation ended.")
                break

            reply = process_query(user_text)
            log(f"🤖 Sofi: {reply}")

            remember(user_text, reply)
            speak(reply)


if __name__ == "__main__":
    run()
