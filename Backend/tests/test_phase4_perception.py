import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.perception.screen import screen_perception
from services.perception.ocr import ocr_engine
from services.perception.code_sandbox import code_sandbox

def test_phase4_perception():
    print("--- Testing Phase 4 Perception Suite ---")

    # 1. Test Screen Capture
    img, path = screen_perception.capture_screen_image("test_capture.png")
    print(f"Captured screen size: {img.size}, path: {path}")
    assert img.size[0] > 0 and img.size[1] > 0
    print("[PASSED] Screen Perception test")

    # 2. Test OCR Engine
    text = ocr_engine.read_screen_now()
    print(f"Extracted Screen OCR Text ({len(text)} chars):\n{text[:200]}...")
    assert isinstance(text, str)
    print("[PASSED] OCR Engine test")

    # 3. Test Code Execution Sandbox
    python_snippet = "a = 21\nb = 21\nprint(f'Result: {a + b}')"
    res = code_sandbox.execute_python_code(python_snippet)
    print(f"Sandbox execution output: {res}")
    assert res["status"] == "success"
    assert "Result: 42" in res["stdout"]
    print("[PASSED] Code Sandbox Execution test")

    print("\n[PASSED] ALL Phase 4 Perception Unit Tests Successful!")

if __name__ == "__main__":
    test_phase4_perception()
