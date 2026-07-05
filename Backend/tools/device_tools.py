# tools/device_tools.py

import os
import subprocess
import ctypes
from PIL import ImageGrab
import win32clipboard
import psutil
import base64

# For Pycaw Volume Control
from ctypes import cast, POINTER
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    pass  # Will be handled gracefully or installed by user

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


def _set_radio_state(kind: str, state: str) -> bool:
    """kind should be 'WiFi' or 'Bluetooth', state should be 'On' or 'Off'"""
    ps_script = f"""
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
    Function Await($WinRtTask, $ResultType) {{
        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
        $netTask = $asTask.Invoke($null, @($WinRtTask))
        $netTask.Wait(-1) | Out-Null
        $netTask.Result
    }}
    [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
    [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
    Await ([Windows.Devices.Radios.Radio]::RequestAccessAsync()) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
    $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
    $target = $radios | Where-Object {{ $_.Kind -eq '{kind}' }}
    if ($target) {{
        Await ($target.SetStateAsync('{state}')) ([Windows.Devices.Radios.RadioAccessStatus]) | Out-Null
        exit 0
    }} else {{
        exit 1
    }}
    """
    encoded_script = base64.b64encode(ps_script.encode('utf-16le')).decode('ascii')
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded_script],
            capture_output=True,
            text=True
        )
        return res.returncode == 0
    except Exception:
        return False


# ---------------------------------------------------------
#  VOLUME CONTROL
# ---------------------------------------------------------

def _get_audio_interface():
    try:
        import comtypes
        comtypes.CoInitialize()
    except Exception:
        pass
        
    devices = AudioUtilities.GetSpeakers()
    return devices.EndpointVolume

def set_volume(level: int, *args, **kwargs) -> str:
    level = max(0, min(level, 100))

    try:
        volume = _get_audio_interface()
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except Exception as e:
        return f"Couldn't adjust volume: {e}"


def mute_volume(*args, **kwargs) -> str:
    try:
        volume = _get_audio_interface()
        volume.SetMute(1, None)
        return "Muted the volume."
    except Exception as e:
        return f"Couldn't mute the volume: {e}"


# ---------------------------------------------------------
#  BRIGHTNESS CONTROL
# ---------------------------------------------------------

def set_brightness(level: int, *args, **kwargs) -> str:
    level = max(0, min(level, 100))
    success, _ = run_powershell(
        f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
    )
    return f"Brightness set to {level}%." if success else "Couldn't change brightness on this device."


# ---------------------------------------------------------
#  WIFI CONTROL (Dynamic Adapter Detection)
# ---------------------------------------------------------

def wifi_off(*args, **kwargs) -> str:
    success = _set_radio_state("WiFi", "Off")
    return "WiFi is now turned OFF!" if success else "Couldn't turn off WiFi."


def wifi_on(*args, **kwargs) -> str:
    success = _set_radio_state("WiFi", "On")
    return "WiFi is now turned ON!" if success else "Couldn't turn on WiFi."


# ---------------------------------------------------------
#  BLUETOOTH CONTROL (Official Windows API)
# ---------------------------------------------------------

def bluetooth_on(*args, **kwargs) -> str:
    success = _set_radio_state("Bluetooth", "On")
    return "Bluetooth is now ON!" if success else "Couldn't turn on Bluetooth."


def bluetooth_off(*args, **kwargs) -> str:
    success = _set_radio_state("Bluetooth", "Off")
    return "Bluetooth is now OFF!" if success else "Couldn't turn off Bluetooth."


# ---------------------------------------------------------
#  SCREENSHOT
# ---------------------------------------------------------

def take_screenshot(path="C:/Users/ASUS/Downloads/screenshot.png", *args, **kwargs) -> str:
    try:
        img = ImageGrab.grab()
        img.save(path)
        return f"Screenshot saved to {path}"
    except:
        return "Failed to capture screenshot."


# ---------------------------------------------------------
#  CLIPBOARD
# ---------------------------------------------------------

def get_clipboard(*args, **kwargs) -> str:
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except:
        return "Clipboard is empty or unreadable."


def set_clipboard(text: str, *args, **kwargs) -> str:
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

def lock_system(*args, **kwargs) -> str:
    ctypes.windll.user32.LockWorkStation()
    return "Locking the system."


def shutdown(*args, **kwargs) -> str:
    os.system("shutdown /s /t 0")
    return "Shutting down your PC."


def restart(*args, **kwargs) -> str:
    os.system("shutdown /r /t 0")
    return "Restarting your PC."


# ---------------------------------------------------------
#  SYSTEM INFO
# ---------------------------------------------------------

def get_system_info(*args, **kwargs) -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "battery_percent": psutil.sensors_battery().percent if psutil.sensors_battery() else "No battery detected"
    }


# ---------------------------------------------------------
#  ADDITIONAL PC INTEGRATIONS
# ---------------------------------------------------------

def close_app(app_name: str, *args, **kwargs) -> str:
    """Fuzzy find and terminate running processes with the given name."""
    app_name_lower = app_name.lower().strip()
    terminated_count = 0
    terminated_names = set()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pinfo = proc.info
            pname = pinfo['name']
            if pname:
                pname_lower = pname.lower()
                # If app_name is a substring of process name (e.g. "chrome" in "chrome.exe")
                # or vice-versa
                if app_name_lower in pname_lower or pname_lower.startswith(app_name_lower):
                    proc.terminate()
                    terminated_count += 1
                    terminated_names.add(pname)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    if terminated_count > 0:
        return f"Terminated {terminated_count} process(es): {', '.join(terminated_names)}."
    else:
        return f"No running processes found matching '{app_name}'."


def empty_recycle_bin(*args, **kwargs) -> str:
    """Empty the Windows Recycle Bin."""
    try:
        # 7 = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        # 0x80004005 is E_FAIL, which can happen if the bin is already empty
        if result == 0 or result == -2147467259:  # 0x80004005 is -2147467259 in signed 32-bit
            return "Recycle bin emptied successfully."
        else:
            return f"Recycle bin empty process returned status {result}."
    except Exception as e:
        return f"Could not empty recycle bin: {e}"


def get_disk_space(*args, **kwargs) -> str:
    """Return total and free disk space for local drives."""
    drives_info = []
    for partition in psutil.disk_partitions():
        if 'fixed' in partition.opts or partition.fstype:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                free_gb = usage.free / (1024**3)
                total_gb = usage.total / (1024**3)
                drives_info.append(
                    f"Drive {partition.mountpoint} ({partition.fstype}): {free_gb:.1f} GB free of {total_gb:.1f} GB ({usage.percent}% used)"
                )
            except PermissionError:
                continue
    if drives_info:
        return "\n".join(drives_info)
    return "Could not retrieve disk space info."

