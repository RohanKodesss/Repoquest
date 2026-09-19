"""
map_builder.py — Build the dungeon map from repo data.

build_map(repo_data) → dict | raises ValueError

Map constants (adjust at top of file only):
  MIN_FILES_FOR_ROOM = 3   (PRD v3.0)
  MAX_ROOMS = 12           (Spec v5.1 / API Spec Rev 4)

The returned dict is the full game object with narration=null.
Connectivity check is inside this module (not a separate file).

Wired in: Step 3
"""

# Map shape constants (PRD v3.0 and API Spec Rev 4)
MIN_FILES_FOR_ROOM = 3
MAX_ROOMS = 12


def build_map(repo_data: dict) -> dict:
    """
    Build and return the game map from repo_data.
    repo_data keys: description, readme, tree, issues, dependencies.
    Raises ValueError if the map cannot be built (not connected, no rooms).
    Implemented in Step 3.
    """
    raise NotImplementedError("map_builder.build_map — implemented in Step 3")
