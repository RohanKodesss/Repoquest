"""
cache.py — Save and load game JSON files.

One file per repo: cache/owner-repo.json
The folder is created on first save.
A missing, empty, or corrupt file returns None (triggers a rebuild).
"""

import json
import os

CACHE_DIR = "cache"


def _path(owner: str, repo: str) -> str:
    """Build the cache file path from validated owner and repo strings."""
    return os.path.join(CACHE_DIR, f"{owner}-{repo}.json")


def load(owner: str, repo: str) -> dict | None:
    """
    Return the saved game dict, or None if the file does not exist,
    is empty, or is not valid JSON.
    """
    try:
        with open(_path(owner, repo), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def save(owner: str, repo: str, game: dict) -> None:
    """Write the game dict to the cache file, creating the folder if needed."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_path(owner, repo), "w", encoding="utf-8") as f:
        json.dump(game, f, indent=2, ensure_ascii=False)
