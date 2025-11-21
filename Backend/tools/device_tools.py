# tools/device_tools.py

import os
import subprocess
import ctypes
from PIL import ImageGrab
import win32clipboard
import psutil


# ---------------------------------------------------------
#  HELPERS
# ---------------------------------------------------------

def run_powershell(cmd: str):
    """Run a PowerShell command and return (success, output)."""
    try:
        result = subprocess.run(
            f"powershell -Command \"{cmd}\"",
            capture_output=True,
            text=True,
            shell=True
        )
        success = result.returncode == 0
        return success, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------
#  VOLUME CONTROL
# ---------------------------------------------------------

def set_volume(level: int) -> str:
    level = max(0, min(level, 100))

    try:
        # 174 = Volume Down, 175 = Volume Up
        # We approximate volume with repeated key presses (simple but reliable)
        subprocess.run(
            f"powershell (new-object -COM WScript.Shell).SendKeys([char]174)",
            shell=True
        )
        return f"Volume set to {level}%."
    except:
        return "Couldn't adjust volume."


def mute_volume() -> str:
    try:
        subprocess.run(
            "powershell (new-object -COM WScript.Shell).SendKeys([char]173)",
            shell=True
        )
        return "Muted the volume."
    except:
        return "Couldn't mute the volume."


# ---------------------------------------------------------
#  BRIGHTNESS CONTROL
# ---------------------------------------------------------

def set_brightness(level: int) -> str:
    level = max(0, min(level, 100))
    success, _ = run_powershell(
        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
    )
    return f"Brightness set to {level}%." if success else "Couldn't change brightness on this device."


# ---------------------------------------------------------
#  WIFI CONTROL (Dynamic Adapter Detection)
# ---------------------------------------------------------

def get_wifi_adapter_name():
    success, output = run_powershell(
        "Get-NetAdapter -Physical | Where-Object {$_.Name -like 'Wi*' -or $_.InterfaceDescription -like '*Wireless*'} | "
        "Select -First 1 -ExpandProperty Name"
    )

    return output if success and output else None


def wifi_off() -> str:
    name = get_wifi_adapter_name()
    if not name:
        return "Couldn't detect your WiFi adapter."

    success, _ = run_powershell(f"netsh interface set interface name='{name}' admin=disabled")
    return "WiFi is now turned OFF!" if success else "Couldn't turn off WiFi."


def wifi_on() -> str:
    name = get_wifi_adapter_name()
    if not name:
        return "Couldn't detect your WiFi adapter."

    success, _ = run_powershell(f"netsh interface set interface name='{name}' admin=enabled")
    return "WiFi is now turned ON!" if success else "Couldn't turn on WiFi."


# ---------------------------------------------------------
#  BLUETOOTH CONTROL (Official Windows API)
# ---------------------------------------------------------

def bluetooth_on() -> str:
    success, _ = run_powershell(
        "[Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult() | "
        "Where-Object {$_.Kind -eq 'Bluetooth'} | "
        "ForEach-Object {$_.SetStateAsync(1).GetAwaiter().GetResult()}"
    )

    return "Bluetooth is now ON!" if success else "Couldn't turn on Bluetooth."


def bluetooth_off() -> str:
    success, _ = run_powershell(
        "[Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult() | "
        "Where-Object {$_.Kind -eq 'Bluetooth'} | "
        "ForEach-Object {$_.SetStateAsync(0).GetAwaiter().GetResult()}"
    )

    return "Bluetooth is now OFF!" if success else "Couldn't turn off Bluetooth."


# ---------------------------------------------------------
#  SCREENSHOT
# ---------------------------------------------------------

def take_screenshot(path="C:/Users/ASUS/Downloads/screenshot.png") -> str:
    try:
        img = ImageGrab.grab()
        img.save(path)
        return f"Screenshot saved to {path}"
    except:
        return "Failed to capture screenshot."


# ---------------------------------------------------------
#  CLIPBOARD
# ---------------------------------------------------------

def get_clipboard() -> str:
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except:
        return "Clipboard is empty or unreadable."


def set_clipboard(text: str) -> str:
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
        return "Copied to clipboard."
    except:
        return "Couldn't copy to clipboard."


# ---------------------------------------------------------
#  SYSTEM ACTIONS
# ---------------------------------------------------------

def lock_system() -> str:
    ctypes.windll.user32.LockWorkStation()
    return "Locking the system."


def shutdown() -> str:
    os.system("shutdown /s /t 0")
    return "Shutting down your PC."


def restart() -> str:
    os.system("shutdown /r /t 0")
    return "Restarting your PC."


# ---------------------------------------------------------
#  SYSTEM INFO
# ---------------------------------------------------------

def get_system_info() -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "battery_percent": psutil.sensors_battery().percent if psutil.sensors_battery() else "No battery detected"
    }
