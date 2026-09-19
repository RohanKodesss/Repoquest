"""
name_validator.py — Catch fake repo names in LLM output.

build_known_names(tree_paths, dependencies) → set[str]
validate_names(text, tree_paths, dependencies) → {"invalid": list[str]}

Checks:
  1. Every token the LLM wrapped in backticks
  2. Tokens ending in a known file extension (.py, .md, .json, etc.)
  3. Slash-path tokens whose first segment is a real folder or file name

Does NOT check:
  - Plain prose words
  - Slash-paths whose first segment is not in the real tree
    (so "and/or" in prose is never flagged)
"""

from __future__ import annotations
import re

# Tokens the LLM wrapped in backticks.
_BACKTICKED = re.compile(r"`([^`\n]+)`")

# Known file extensions that trigger a check.
_EXTENSIONS = (
    "py|js|ts|jsx|tsx|md|json|txt|yml|yaml|toml|html|css|"
    "java|go|rs|c|cpp|h|sh|cfg|ini|lock|mod|sum|gradle|xml|rb|php"
)
_FILE_LIKE = re.compile(rf"\b[\w\-./]+\.(?:{_EXTENSIONS})\b")

# Slash-path tokens: word characters and common name chars separated by slashes.
_SLASH_PATH = re.compile(r"[\w.\-]+(?:/[\w.\-]+)+/?")


def build_known_names(
    tree_paths: list[str],
    dependencies: tuple[str, ...] | list[str] = (),
) -> set[str]:
    """
    Build a set of everything real in the repo:
    full paths, every folder prefix, individual file/folder names,
    and dependency package names.
    """
    known: set[str] = set(dependencies)
    for path in tree_paths:
        parts = path.rstrip("/").split("/")
        for i in range(1, len(parts) + 1):
            known.add("/".join(parts[:i]))  # every folder prefix + full path
        known.update(parts)                 # individual names
    return known


def validate_names(
    text: str,
    tree_paths: list[str],
    dependencies: tuple[str, ...] | list[str] = (),
) -> dict:
    """
    Return {"invalid": [...]} listing names in text that are not in the repo.
    Only backticked tokens, file-extension tokens, and slash-paths whose
    first segment is real are checked. Plain prose is not checked.
    """
    known = build_known_names(tree_paths, dependencies)

    checked: set[str] = set()
    checked.update(_BACKTICKED.findall(text))
    checked.update(_FILE_LIKE.findall(text))

    for token in _SLASH_PATH.findall(text):
        first = token.strip("/.,;:").split("/")[0]
        if first in known:
            checked.add(token)

    # Strip trailing punctuation before checking membership.
    invalid = sorted(
        t for t in checked if t.rstrip("/.,;:") not in known
    )
    return {"invalid": invalid}
