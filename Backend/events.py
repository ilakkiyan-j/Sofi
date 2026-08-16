import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Awaitable, Any, Set
from tools.logger import log

@dataclass
class Event:
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

# Standard System Event Topics
EVENT_STT_PARTIAL = "stt.partial"
EVENT_STT_FINAL = "stt.final"
EVENT_LLM_FIRST_TOKEN = "llm.first_token"
EVENT_LLM_TOKEN = "llm.token"
EVENT_TOOL_START = "tool.start"
EVENT_TOOL_FINISH = "tool.finish"
EVENT_TTS_CHUNK = "tts.chunk"
EVENT_VOICE_INTERRUPT = "voice.interrupt"


class AsyncEventBus:
    """
    Decoupled Async Pub/Sub Event Bus for real-time streaming components.
    """
    def __init__(self):
        self._subscribers: Dict[str, Set[Callable[[Event], Awaitable[None]]]] = {}

    def subscribe(self, topic: str, handler: Callable[[Event], Awaitable[None]]):
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(handler)

    def unsubscribe(self, topic: str, handler: Callable[[Event], Awaitable[None]]):
        if topic in self._subscribers:
            self._subscribers[topic].discard(handler)

    async def publish(self, topic: str, payload: Dict[str, Any] = None):
        if payload is None:
            payload = {}
        event = Event(topic=topic, payload=payload)
        
        if topic in self._subscribers:
            tasks = [
                asyncio.create_task(self._safe_execute(handler, event))
                for handler in self._subscribers[topic]
            ]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler: Callable[[Event], Awaitable[None]], event: Event):
        try:
            await handler(event)
        except Exception as e:
            log(f"🔴 EventBus Error in [{event.topic}]: {e}")

# Global singleton event bus instance
event_bus = AsyncEventBus()
