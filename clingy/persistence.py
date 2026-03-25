"""JSON file persistence for sticky notes.

Notes are stored as individual JSON files in ~/.local/share/clingy/.
Writes are atomic (write to temp file, then rename) to prevent corruption.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


def get_data_dir() -> Path:
    """Return the data directory, creating it if it does not exist.

    Uses ~/.local/share/clingy/ following the XDG Base Directory spec.
    Respects $XDG_DATA_HOME if set.
    """
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        base = Path(xdg_data)
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / "clingy"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _note_path(note_id: str) -> Path:
    """Return the file path for a note's JSON file."""
    return get_data_dir() / f"note_{note_id}.json"


def save_note(note_id: str, data: dict) -> None:
    """Save a single note's data to disk atomically.

    Args:
        note_id: The UUID string identifying the note.
        data: A dictionary containing the note's serialisable state.
    """
    data["modified_at"] = datetime.now().isoformat()
    path = _note_path(note_id)
    data_dir = path.parent

    # Write to a temporary file in the same directory, then atomically rename.
    fd, tmp_path = tempfile.mkstemp(dir=data_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up the temp file on failure.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def load_all_notes() -> list[dict]:
    """Load all saved notes from the data directory.

    Returns:
        A list of note data dicts.  Malformed files are skipped with a
        warning printed to stderr.
    """
    data_dir = get_data_dir()
    notes: list[dict] = []
    for path in sorted(data_dir.glob("note_*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "id" in data:
                notes.append(data)
            else:
                print(f"clingy: skipping invalid note file: {path}")
        except (json.JSONDecodeError, OSError) as exc:
            print(f"clingy: skipping malformed note file {path}: {exc}")
    return notes


def delete_note_file(note_id: str) -> None:
    """Delete the JSON file for a given note, if it exists."""
    path = _note_path(note_id)
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        print(f"clingy: failed to delete {path}: {exc}")
