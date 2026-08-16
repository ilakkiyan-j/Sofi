# Sample Sofi Extension Plugin

def get_system_uptime():
    """Sample custom tool function."""
    import time
    return f"System active session uptime: {int(time.process_time())} seconds."

SOFI_PLUGIN = {
    "name": "get_system_uptime",
    "function": get_system_uptime,
    "schema": {
        "type": "function",
        "function": {
            "name": "get_system_uptime",
            "description": "Returns current Sofi backend system uptime statistics.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
}
