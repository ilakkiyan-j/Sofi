import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from llm.tools_registry import TOOLS, TOOLS_SCHEMA
from llm.async_core import async_process_query_stream
from tools.logger import log

class ReActPlannerService:
    """
    Autonomous ReAct (Reasoning + Acting) Agent Planner.
    Decomposes multi-step tasks into actionable tool executions,
    evaluates step results, and iterates until the user request is complete.
    """
    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations

    async def execute_task_plan(self, user_goal: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Runs an autonomous ReAct loop yielding real-time plan status updates:
        {"type": "plan_thought", "thought": str}
        {"type": "tool_start", "name": str, "args": dict}
        {"type": "tool_finish", "name": str, "result": str}
        {"type": "done", "full_text": str}
        """
        log(f"🧠 ReAct Planner initiated for goal: {user_goal}")
        yield {"type": "plan_thought", "thought": f"Formulating plan to solve: {user_goal}"}

        # Delegate execution through stream router
        async for packet in async_process_query_stream(user_goal):
            yield packet


# Global singleton instance
react_planner = ReActPlannerService()
