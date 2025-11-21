import os
from pathlib import Path
from typing import Optional
from config import USER_FILES_DIR
from tools.logger import log

# Windows standard folders
USER_HOME = Path.home()
SPECIAL_FOLDERS = {
    "downloads": USER_HOME / "Downloads",
    "documents": USER_HOME / "Documents",
    "desktop": USER_HOME / "Desktop",
    "pictures": USER_HOME / "Pictures",
    "photos": USER_HOME / "Pictures",
    "music": USER_HOME / "Music",
    "videos": USER_HOME / "Videos",
}

BASE_DIR = Path(USER_FILES_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)


def _full_path(filename: str) -> Path:
    # basic sanitization
    filename = filename.strip()
    # prevent path traversal
    filename = filename.replace("..", "")
    return BASE_DIR / filename


def list_files(folder: str = "") -> str:
    folder_path = BASE_DIR if folder == "" else (BASE_DIR / folder)
    if not folder_path.exists():
        return f"Folder '{folder}' does not exist."

    items = [p.name for p in folder_path.iterdir()]
    if not items:
        return "The folder is empty."
    return "\n".join(items)


def read_file(filename: str) -> str:
    path = _full_path(filename)
    if not path.exists():
        return f"File '{filename}' not found."

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


def create_file(filename: str) -> str:
    path = _full_path(filename)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return f"Created file '{filename}'."
    except Exception as e:
        return f"Error creating file: {e}"


def write_file(filename: str, content: str) -> str:
    path = _full_path(filename)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or "", encoding="utf-8")
        return f"Wrote to '{filename}'."
    except Exception as e:
        return f"Error writing to file: {e}"


def append_file(filename: str, content: str) -> str:
    path = _full_path(filename)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            if content:
                f.write("\n" + content)
        return f"Appended to '{filename}'."
    except Exception as e:
        return f"Error appending to file: {e}"


def delete_file(filename: str) -> str:
    path = _full_path(filename)
    if not path.exists():
        return f"File '{filename}' does not exist."
    try:
        path.unlink()
        return f"Deleted '{filename}'."
    except Exception as e:
        return f"Error deleting file: {e}"

def resolve_path(user_text: str) -> Path:
    """
    Convert natural language input into a real path.
    Examples:
        'downloads' → C:/Users/.../Downloads
        'folder test inside downloads' → Downloads/test
    """

    text = user_text.lower().strip()

    # 1. detect which base folder
    base = None
    for name, folder in SPECIAL_FOLDERS.items():
        if name in text:
            base = folder
            break

    # if no special folder, fallback to USER_FILES_DIR
    if base is None:
        return BASE_DIR / user_text.replace(" ", "_")

    # 2. detect nested folder: "inside X"
    # Example: "open photos inside downloads"
    if "inside" in text:
        try:
            parts = text.split("inside")
            nested_part = parts[0].strip()     # before "inside"
            nested_part = (
                nested_part.replace("open", "")
                           .replace("folder", "")
                           .replace("the", "")
                           .strip()
            )
            return base / nested_part
        except:
            return base

    # if simply "open downloads"
    return base

def open_path(path: str) -> str:
    resolved = resolve_path(path)
    log(resolved)
    if not resolved.exists():
        return f"Folder or file '{path}' does not exist."

    try:
        os.startfile(resolved)
        return f"Opening {resolved.name}."
    except Exception as e:
        return f"Could not open '{resolved}': {e}"


