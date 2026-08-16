import re
from typing import Generator, List

class SentenceChunker:
    """
    Buffers streaming LLM tokens and yields complete sentences or clauses 
    as soon as sentence boundary punctuation (. ! ? ; \n) is encountered.
    This enables low-latency sentence-by-sentence TTS synthesis.
    """
    def __init__(self, min_sentence_length: int = 12):
        self.buffer = ""
        self.min_sentence_length = min_sentence_length
        self.punctuation_pattern = re.compile(r'([.!?;:\n])')

    def push(self, token: str) -> List[str]:
        """
        Pushes a new token into the buffer and returns any completed sentence chunks.
        """
        self.buffer += token
        chunks = []

        while True:
            match = self.punctuation_pattern.search(self.buffer)
            if not match:
                break

            idx = match.end()
            candidate = self.buffer[:idx].strip()
            
            # Ensure candidate meets minimum length threshold to avoid ultra-short fragments (e.g., "Mr.", "1.")
            # unless buffer is getting very long
            if len(candidate) >= self.min_sentence_length or len(self.buffer) > 100:
                chunks.append(candidate)
                self.buffer = self.buffer[idx:].lstrip()
            else:
                # Keep buffering if too short
                break

        return chunks

    def flush(self) -> str:
        """
        Flushes any remaining text in the buffer when LLM generation completes.
        """
        remaining = self.buffer.strip()
        self.buffer = ""
        return remaining
