import sys
import numpy as np
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.tts.sentence_chunker import SentenceChunker
from services.tts.piper_stream import StreamingTTSEngine
from services.stt.whisper_stt import FasterWhisperSTT

def test_phase2_voice_pipeline():
    print("--- Testing Phase 2 Voice Pipeline ---")

    # 1. Test Sentence Chunker
    chunker = SentenceChunker()
    tokens = ["Sofi ", "is ", "an ", "offline ", "AI ", "assistant. ", "It ", "runs ", "fast!"]
    chunks = []
    for token in tokens:
        chunks.extend(chunker.push(token))
    remaining = chunker.flush()
    if remaining:
        chunks.append(remaining)
    
    print(f"Chunks generated: {chunks}")
    assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
    print("[PASSED] Sentence Chunker test")

    # 2. Test TTS Engine Fallback & Interruption
    tts = StreamingTTSEngine()
    tts.interrupt()
    assert tts.is_interrupted == True
    tts.reset_interruption()
    assert tts.is_interrupted == False
    print("[PASSED] Streaming TTS Engine test")

    # 3. Test STT VAD Barge-In Volume Check
    stt = FasterWhisperSTT()
    dummy_silence = np.zeros(320, dtype=np.int16).tobytes()
    has_speech, volume = stt.process_voice_chunk(dummy_silence, is_tts_speaking=False)
    assert has_speech == False, "Silence misidentified as speech"
    
    dummy_voice = (np.sin(np.linspace(0, 100, 320)) * 20000).astype(np.int16).tobytes()
    has_speech, volume = stt.process_voice_chunk(dummy_voice, is_tts_speaking=False)
    assert has_speech == True, "Voice audio misidentified as silence"
    print("[PASSED] FasterWhisper STT VAD test")

    print("\n[PASSED] ALL Phase 2 Voice Pipeline Unit Tests Successful!")

if __name__ == "__main__":
    test_phase2_voice_pipeline()
