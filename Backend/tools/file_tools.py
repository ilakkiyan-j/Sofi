import os
from pathlib import Path
from typing import Optional
from config import USER_FILES_DIR

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
