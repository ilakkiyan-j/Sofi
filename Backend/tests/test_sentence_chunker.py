import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.tts.sentence_chunker import SentenceChunker

def test_sentence_chunker():
    chunker = SentenceChunker(min_sentence_length=10)
    tokens = ["Hello ", "there, ", "I am Sofi! ", "How ", "can I ", "help you ", "today?"]
    
    chunks = []
    for token in tokens:
        res = chunker.push(token)
        if res:
            chunks.extend(res)
            
    remaining = chunker.flush()
    if remaining:
        chunks.append(remaining)
        
    print(f"Extracted Chunks: {chunks}")
    assert len(chunks) >= 2
    assert "Hello there, I am Sofi!" in chunks[0]
    print("[PASSED] SentenceChunker test")

if __name__ == "__main__":
    test_sentence_chunker()
