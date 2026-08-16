from tools.file_tools import (
    list_files,
    read_file,
    create_file,
    write_file,
    append_file,
    delete_file,
    open_path
)

from tools.web_tools import search_web
from tools.app_tools import launch_app

# NEW DEVICE AUTOMATION IMPORTS
from tools.device_tools import (
    set_volume,
    mute_volume,
    set_brightness,
    wifi_on,
    wifi_off,
    bluetooth_on,
    bluetooth_off,
    take_screenshot,
    get_clipboard,
    set_clipboard,
    lock_system,
    shutdown,
    restart,
    get_system_info,
    close_app,
    empty_recycle_bin,
    get_disk_space
)

from services.perception.ocr import ocr_engine
from services.perception.code_sandbox import code_sandbox

def read_screen_text():
    """Extracts all visible text on user's screen using RapidOCR."""
    return ocr_engine.read_screen_now()

def run_python_code(code: str):
    """Executes a Python code snippet in an isolated sandbox and returns stdout/stderr."""
    res = code_sandbox.execute_python_code(code)
    if res["status"] == "success":
        return f"[Output]:\n{res['stdout']}"
    else:
        return f"[{res['status'].upper()}]:\n{res['stderr']}"

TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "create_file": create_file,
    "write_file": write_file,
    "append_file": append_file,
    "delete_file": delete_file,
    "search_web": search_web,
    "open_path": open_path,
    "launch_app": launch_app,
    "read_screen_text": read_screen_text,
    "run_python_code": run_python_code,

    # DEVICE AUTOMATION LAYER
    "set_volume": set_volume,
    "mute_volume": mute_volume,
    "set_brightness": set_brightness,
    "wifi_on": wifi_on,
    "wifi_off": wifi_off,
    "bluetooth_on": bluetooth_on,
    "bluetooth_off": bluetooth_off,
    "take_screenshot": take_screenshot,
    "get_clipboard": get_clipboard,
    "set_clipboard": set_clipboard,
    "lock_system": lock_system,
    "shutdown": shutdown,
    "restart": restart,
    "get_system_info": get_system_info,
    "close_app": close_app,
    "empty_recycle_bin": empty_recycle_bin,
    "get_disk_space": get_disk_space
}


TOOLS_SCHEMA = [

    # -------------------- FILE TOOLS --------------------
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files stored in Sofi's user_files directory.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create an empty file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Overwrite the file with new content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "Append content to an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file permanently.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"]
            }
        }
    },

    # -------------------- WEB SEARCH --------------------
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web using DuckDuckGo for facts, news, and real-time info. NEVER call this tool for general chat, greetings, questions about your own identity (like 'who are you', 'how are you', 'what can you do', 'tell me about yourself'), or local tasks/device settings adjustments.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },

    # -------------------- FILE EXPLORER --------------------
    {
        "type": "function",
        "function": {
            "name": "open_path",
            "description": "Open a folder or file using the OS file explorer.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },

    # -------------------- APP LAUNCHING --------------------
    {
        "type": "function",
        "function": {
            "name": "launch_app",
            "description": "Open ANY installed app dynamically using fuzzy matching and system scanning.",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string"}},
                "required": ["app_name"]
            }
        }
    },

    # ======================================================
    #              DEVICE AUTOMATION SCHEMA
    # ======================================================

    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set system speaker volume level (0-100). Call this for any requests to change, increase, decrease, adjust, or set the volume.",
            "parameters": {
                "type": "object",
                "properties": {"level": {"type": "number"}},
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mute_volume",
            "description": "Mute the system volume.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Set system/monitor screen brightness level (0-100). Call this for any request to adjust, dim, increase, decrease, or set the PC screen brightness.",
            "parameters": {
                "type": "object",
                "properties": {"level": {"type": "number"}},
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wifi_on",
            "description": "Enable the WiFi adapter.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wifi_off",
            "description": "Disable the WiFi adapter.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bluetooth_on",
            "description": "Turn on Bluetooth.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bluetooth_off",
            "description": "Turn off Bluetooth.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot and save it to a default path.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clipboard",
            "description": "Return text currently stored in clipboard.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_clipboard",
            "description": "Copy text to clipboard.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lock_system",
            "description": "Lock the system immediately.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown",
            "description": "Shut down the system.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart",
            "description": "Restart the system.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get CPU, RAM, and Battery levels.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Close a running PC application or process. Call this when the user asks to close, terminate, exit, or kill a specific program.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "The name of the application to close (e.g. 'chrome', 'notepad')."}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "empty_recycle_bin",
            "description": "Empty the Windows Recycle Bin.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_space",
            "description": "Get storage metrics, total/free disk space for C: and other local drives on the PC.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_screen_text",
            "description": "Read and extract all visible text currently displayed on the user's screen using high-speed OCR. Call this whenever the user asks 'what is on my screen', 'read my screen', 'summarize what's open', etc.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": "Run a Python script in a sandboxed process and return the output. Call this when asked to write and run code, execute math/data scripts, or test Python snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The Python code snippet to execute."}
                },
                "required": ["code"]
            }
        }
    }
]
