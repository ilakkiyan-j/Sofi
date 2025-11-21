# tools/app_tools.py

import os
import json
import subprocess
from pathlib import Path
from fuzzywuzzy import process

USER = os.getenv("USERNAME")

START_MENU_PATHS = [
    fr"C:\Users\{USER}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
]

app_index = {}           # For .lnk apps → { "chrome": "C:/.../chrome.lnk" }
uwp_app_index = {}       # For UWP apps → { "whatsapp": "AppID" }


# ---------------------------------------------
#   START MENU DESKTOP APPS (.lnk)
# ---------------------------------------------
def index_start_menu():
    for base in START_MENU_PATHS:
        if not os.path.exists(base):
            continue

        for root, dirs, files in os.walk(base):
            for file in files:
                if file.endswith(".lnk"):
                    name = Path(file).stem.lower()
                    full = os.path.join(root, file)
                    app_index[name] = full


# ---------------------------------------------
#   UWP + Microsoft Store Apps (Dynamic)
# ---------------------------------------------
def index_uwp_apps():
    try:
        raw = subprocess.check_output(
            'powershell "Get-StartApps | ConvertTo-Json"',
            shell=True
        )

        apps = json.loads(raw)

        # When only one app is returned, it's not a list → wrap it
        if isinstance(apps, dict):
            apps = [apps]

        for item in apps:
            app_name = item.get("Name", "").lower()
            app_id = item.get("AppID", "")
            if app_name and app_id:
                uwp_app_index[app_name] = app_id

    except Exception as e:
        print("Error indexing UWP apps:", e)


# ---------------------------------------------
#   FUZZY SEARCH BETWEEN BOTH SOURCES
# ---------------------------------------------
def fuzzy_find(app_name: str):
    all_choices = list(app_index.keys()) + list(uwp_app_index.keys())

    if not all_choices:
        return None, None

    match, score = process.extractOne(app_name.lower(), all_choices)

    if score < 60:
        return None, None

    # Determine type
    if match in app_index:
        return match, "desktop"
    if match in uwp_app_index:
        return match, "uwp"

    return None, None


# ---------------------------------------------
#   LAUNCH FUNCTIONS
# ---------------------------------------------
def launch_desktop_app(match):
    path = app_index[match]
    try:
        os.startfile(path)
        return f"Opening {match}."
    except Exception as e:
        return f"Found the app but couldn't open it: {e}"


def launch_uwp_app(match):
    app_id = uwp_app_index[match]
    try:
        subprocess.Popen(
            f'explorer.exe shell:AppsFolder\\{app_id}',
            shell=True
        )
        return f"Opening {match}."
    except Exception as e:
        return f"Found the app but couldn't open it: {e}"


# ---------------------------------------------
#   MAIN ENTRY
# ---------------------------------------------
def launch_app(app_name: str) -> str:
    if not app_index:
        index_start_menu()

    if not uwp_app_index:
        index_uwp_apps()

    match, app_type = fuzzy_find(app_name)

    if not match:
        return f"I couldn't find an application named '{app_name}'."

    if app_type == "desktop":
        return launch_desktop_app(match)

    if app_type == "uwp":
        return launch_uwp_app(match)

    return "App found but type not recognized."
