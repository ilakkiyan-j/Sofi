from pathlib import Path

# Project roots
BACKEND_ROOT = Path(__file__).resolve().parent
MODELS_DIR   = BACKEND_ROOT / "models"

# --- Vosk ---
VOSK_MODEL_PATH = MODELS_DIR / "vosk-model-en-us-0.22-lgraph"

# --- Porcupine ---
ACCESS_KEY   = "0ooE6IdBMmlxbVBAVnUUnu5elZO1MBk01nkGzJ42tfxFbcsrSxKOxA=="  # Picovoice AccessKey
WAKEWORD_PPN = BACKEND_ROOT / "wakeword" / "hey-sofi.ppn"     # exact filename you downloaded
SENSITIVITY  = 0.6
