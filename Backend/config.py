from pathlib import Path

# Project roots
BACKEND_ROOT = Path(__file__).resolve().parent
MODELS_DIR   = BACKEND_ROOT / "models"

# Ollama / LLM endpoint
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
LLM_MODEL = "llama3.1"

# TTS model choice for Coqui-TTS (change if you prefer another)
COQUI_TTS_MODEL = "tts_models/en/vctk/vits"

# local folder to store user files
USER_FILES_DIR = BACKEND_ROOT / "user_files"
USER_FILES_DIR.mkdir(exist_ok=True, parents=True)

# --- Vosk ---
VOSK_MODEL_PATH = MODELS_DIR / "vosk-model-en-us-0.22-lgraph"

# --- Porcupine ---
ACCESS_KEY   = "0ooE6IdBMmlxbVBAVnUUnu5elZO1MBk01nkGzJ42tfxFbcsrSxKOxA=="  # Picovoice AccessKey
WAKEWORD_PPN = BACKEND_ROOT / "wakeword" / "hey-sofi.ppn"     # exact filename you downloaded
SENSITIVITY  = 0.6

# memory DB file (simple JSON fallback)
MEMORY_DB = BACKEND_ROOT / "memory_db.json"
