"""
cache.py — Save and load game JSON files.

One file per repo: cache/owner-repo.json
The folder is created on first save.
A missing, empty, or corrupt file returns None (triggers a rebuild).
"""

from __future__ import annotations
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUNDLED_CACHE_DIR = PROJECT_ROOT / "cache"

# Vercel mounts the deployment read-only. /tmp is writable but ephemeral, so it
# is used only as a best-effort runtime cache in production.
if os.getenv("VERCEL"):
    CACHE_DIR = Path(os.getenv("REPOQUEST_CACHE_DIR", "/tmp/repoquest-cache"))
else:
    CACHE_DIR = BUNDLED_CACHE_DIR


def _filename(owner: str, repo: str) -> str:
    """Build the cache file path from validated owner and repo strings."""
    return f"{owner}-{repo}.json"


def _path(owner: str, repo: str) -> Path:
    return CACHE_DIR / _filename(owner, repo)


def load(owner: str, repo: str) -> dict | None:
    """
    Return the saved game dict, or None if the file does not exist,
    is empty, or is not valid JSON.
    """
    paths = [_path(owner, repo)]
    # Demo games are packaged with the function and survive cold starts.
    if CACHE_DIR != BUNDLED_CACHE_DIR:
        paths.append(BUNDLED_CACHE_DIR / _filename(owner, repo))
    for path in paths:
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
    return None


def save(owner: str, repo: str, game: dict) -> None:
    """Write the game dict to the cache file, creating the folder if needed."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with _path(owner, repo).open("w", encoding="utf-8") as f:
        json.dump(game, f, indent=2, ensure_ascii=False)
