"""
repo_check.py — URL parsing and playability checks.

parse_repo_url(url) → (owner, repo) | None
playability_check(tree_items, issues, dependencies) → (ok, warnings, error_info)
"""

from __future__ import annotations
import re

# URL regex matching github.com/owner/repo with support for https, www, .git, subpaths, query, fragment
URL_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/"
    r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:/[^?#]*)?(?:[?#].*)?$"
)

# Playability thresholds (API Spec Rev 4, section 2.2 & note 9)
MIN_REPO_FILES = 5
MIN_REPO_FOLDERS = 2


def parse_repo_url(url: str) -> tuple[str, str] | None:
    """
    Return (owner, repo) or None if the URL is not a plain GitHub repo URL.
    Handles trailing slash, .git, /tree/branch, query params, fragments.
    Rejects directory traversal attempts ('..').
    """
    if not isinstance(url, str):
        return None
    cleaned = url.strip()
    match = URL_PATTERN.match(cleaned)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2)
    if ".." in owner or ".." in repo:
        return None
    return owner, repo


def playability_check(
    tree_items: list[dict],
    issues: list[dict],
    dependencies: list[str] | None,
) -> tuple[bool, list[str], tuple[str, str, int] | None]:
    """
    Check repo contents against playability requirements.
    Returns:
        ok (bool): True if repo is playable.
        warnings (list[str]): Yellow warning messages for missing optional features.
        error_info (tuple[str, str, int] | None): (error_code, message, http_status) if ok is False.
    """
    if not tree_items:
        return False, [], ("empty_repo", "This repo is empty. Try another one.", 422)

    # Count files (blobs) and distinct folders
    files = [item for item in tree_items if item.get("type") == "blob"]
    folders = set()
    for item in tree_items:
        path = item.get("path", "")
        if "/" in path:
            folder = path.rsplit("/", 1)[0]
            if folder:
                folders.add(folder)

    if len(files) < MIN_REPO_FILES or len(folders) < MIN_REPO_FOLDERS:
        return (
            False,
            [],
            (
                "too_small",
                "This repo is too small to build a dungeon. Try a bigger one.",
                422,
            ),
        )

    warnings: list[str] = []

    if len(files) > 100:
        warnings.append("This repo is large. We'll simplify to 12 rooms or fewer.")

    if not issues:
        warnings.append(
            "No open issues found. The largest files guard the dungeon instead."
        )

    if dependencies is None or len(dependencies) == 0:
        warnings.append("No dependency file found. This dungeon has no keys.")

    return True, warnings, None
