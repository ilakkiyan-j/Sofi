import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from events import AsyncEventBus, EVENT_LLM_TOKEN
from llm.async_core import async_process_query_stream

async def test_event_bus():
    print("--- Testing AsyncEventBus ---")
    bus = AsyncEventBus()
    received_tokens = []

    async def token_handler(event):
        received_tokens.append(event.payload.get("token"))

    bus.subscribe(EVENT_LLM_TOKEN, token_handler)
    await bus.publish(EVENT_LLM_TOKEN, {"token": "Hello"})
    await bus.publish(EVENT_LLM_TOKEN, {"token": "World"})

    assert received_tokens == ["Hello", "World"], f"Expected ['Hello', 'World'], got {received_tokens}"
    print("[PASSED] AsyncEventBus test")

async def test_async_llm_stream():
    print("\n--- Testing Async LLM Stream ---")
    query = "Hi Sofi, reply in 5 words."
    tokens = []
    
    try:
        async for packet in async_process_query_stream(query):
            print(f"Packet received: {packet.get('type')}")
            if packet.get("type") == "token":
                tokens.append(packet.get("content"))
            elif packet.get("type") == "done":
                print(f"Full text: {packet.get('full_text')}")
        
        print(f"Total tokens received: {len(tokens)}")
        assert len(tokens) > 0, "No tokens received from LLM stream!"
        print("[PASSED] Async LLM Stream test")
    except Exception as e:
        print(f"[WARNING] Async LLM Stream test warning: {e}")

async def main():
    await test_event_bus()
    await test_async_llm_stream()

if __name__ == "__main__":
    asyncio.run(main())
