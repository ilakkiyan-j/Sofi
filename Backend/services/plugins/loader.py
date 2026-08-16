import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import BACKEND_ROOT
from llm.tools_registry import TOOLS, TOOLS_SCHEMA
from tools.logger import log

class PluginLoaderService:
    """
    Dynamic Plugin Architecture Manager.
    Auto-discovers and registers custom third-party plugins from backend/plugins directory.
    """
    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or (BACKEND_ROOT / "plugins")
        self.plugins_dir.mkdir(exist_ok=True, parents=True)
        self.loaded_plugins: Dict[str, Dict[str, Any]] = {}

    def discover_and_load_plugins(self) -> int:
        """
        Scans backend/plugins directory for .py files exporting `SOFI_PLUGIN` dictionary.
        """
        count = 0
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            plugin_name = file_path.stem
            try:
                spec = importlib.util.spec_from_file_location(plugin_name, file_path)
                if not spec or not spec.loader:
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[plugin_name] = module
                spec.loader.exec_module(module)

                if hasattr(module, "SOFI_PLUGIN"):
                    plugin_info = getattr(module, "SOFI_PLUGIN")
                    func = plugin_info.get("function")
                    schema = plugin_info.get("schema")
                    name = plugin_info.get("name", plugin_name)

                    if func and schema:
                        TOOLS[name] = func
                        TOOLS_SCHEMA.append(schema)
                        self.loaded_plugins[name] = plugin_info
                        count += 1
                        log(f"🔌 Dynamically loaded plugin tool: {name}")

            except Exception as e:
                log(f"⚠️ Failed to load plugin {file_path.name}: {e}")

        return count


# Global singleton instance
plugin_loader = PluginLoaderService()
