import sys
import asyncio
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.plugins.loader import plugin_loader
from services.planner.react import react_planner
from llm.tools_registry import TOOLS

async def test_phase5():
    print("--- Testing Phase 5 ReAct Planner & Plugin System ---")

    # 1. Test Plugin Auto-Discovery & Dynamic Registration
    loaded_count = plugin_loader.discover_and_load_plugins()
    print(f"Plugins Loaded: {loaded_count}")
    assert loaded_count >= 1, "Plugin loader failed to discover sample_plugin.py"
    assert "get_system_uptime" in TOOLS, "Plugin function not found in TOOLS registry!"
    
    uptime_res = TOOLS["get_system_uptime"]()
    print(f"Plugin tool output: {uptime_res}")
    assert "System active session uptime" in uptime_res
    print("[PASSED] Dynamic Plugin Architecture test")

    # 2. Test ReAct Agent Planner Stream
    packets = []
    async for packet in react_planner.execute_task_plan("Check system uptime."):
        packets.append(packet)
        print(f"ReAct packet: {packet.get('type')}")

    assert len(packets) > 0
    print("[PASSED] ReAct Agent Planner test")

    print("\n[PASSED] ALL Phase 5 Planner & Plugin Unit Tests Successful!")

if __name__ == "__main__":
    asyncio.run(test_phase5())
