import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
from tools.logger import log

class CodeSandboxService:
    """
    Isolated Code Execution Sandbox for Sofi Coding Assistant capabilities.
    Runs Python scripts in an isolated subprocess with stdout/stderr capture and timeout protection.
    """
    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def execute_python_code(self, code_str: str) -> Dict[str, Any]:
        """
        Executes Python code snippet and returns execution output dict:
        {"status": "success" | "error" | "timeout", "stdout": str, "stderr": str, "exit_code": int, "duration_ms": float}
        """
        start_time = time.time()
        
        # Write code to a temporary python file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(code_str)
            temp_path = temp_file.name

        try:
            log(f"💻 Running sandboxed Python snippet ({len(code_str)} chars)...")
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            duration_ms = (time.time() - start_time) * 1000.0

            status = "success" if result.returncode == 0 else "error"
            log(f"💻 Code execution {status} in {duration_ms:.1f}ms")

            return {
                "status": status,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode,
                "duration_ms": round(duration_ms, 2)
            }

        except subprocess.TimeoutExpired:
            log(f"⚠️ Code execution timed out after {self.timeout_seconds}s!")
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_seconds} seconds.",
                "exit_code": -1,
                "duration_ms": self.timeout_seconds * 1000.0
            }
        except Exception as e:
            log(f"🔴 Code execution error: {e}")
            return {
                "status": "error",
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "duration_ms": 0.0
            }
        finally:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass


# Global singleton instance
code_sandbox = CodeSandboxService()
