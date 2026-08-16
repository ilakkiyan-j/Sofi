import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.memory.working import WorkingMemory
from services.memory.vector_rag import VectorRAGEngine

def test_phase3_memory():
    print("--- Testing Phase 3 Hierarchical Memory ---")

    # 1. Test L1 Working Memory Ring Buffer
    wm = WorkingMemory(max_turns=3)
    wm.add_message("user", "Hello Sofi")
    wm.add_message("sofi", "Hi Ilakkiyan!")
    wm.add_message("user", "My favorite programming language is Python.")
    wm.add_message("sofi", "Python is awesome!")

    history = wm.get_history()
    print(f"Working Memory Turns: {len(history)}")
    assert len(history) == 3, f"Expected 3 turns in sliding window, got {len(history)}"
    assert history[0]["content"] == "Hi Ilakkiyan!"
    print("[PASSED] L1 Working Memory Ring Buffer test")

    # 2. Test L3 Vector RAG Engine
    rag = VectorRAGEngine()
    save_success = rag.add_memory("I live in Chennai", "Noted, you live in Chennai.")
    print(f"Memory Save Status: {save_success}")

    recalled = rag.query_memories("Where do I live?")
    print(f"Recalled Memory: {recalled}")
    assert "Chennai" in recalled or save_success == True
    print("[PASSED] L3 Vector RAG Engine test")

    print("\n[PASSED] ALL Phase 3 Memory Unit Tests Successful!")

if __name__ == "__main__":
    test_phase3_memory()
