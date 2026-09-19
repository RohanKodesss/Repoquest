"""
test_map_builder.py — Three tests for map_builder.py.

Run with: python -m pytest tests/test_map_builder.py -v
(Use python -m pytest, not plain pytest, so Python finds the modules/ folder.)

These tests will be skipped (NotImplementedError) until Step 3.
They are written now so the expected behaviour is pinned.
"""

import pytest
from modules.map_builder import build_map

# Shared sample repo_data — two real folders, no issues.
SAMPLE = {
    "description": "A sample project",
    "readme": "Hello world.",
    "tree": [
        {"path": "README.md",           "type": "blob", "size": 50},
        {"path": "src/app.py",          "type": "blob", "size": 500},
        {"path": "src/utils.py",        "type": "blob", "size": 200},
        {"path": "src/helpers.py",      "type": "blob", "size": 150},
        {"path": "tests/test_app.py",   "type": "blob", "size": 100},
        {"path": "tests/conftest.py",   "type": "blob", "size": 60},
        {"path": "tests/test_utils.py", "type": "blob", "size": 80},
    ],
    "issues": [],
    "dependencies": [],
}


def _reachable(game_map: dict) -> set:
    """Walk exits from the start room. Return every reachable room ID."""
    seen, todo = set(), [game_map["start"]]
    while todo:
        room = todo.pop()
        if room in seen:
            continue
        seen.add(room)
        todo.extend(game_map["rooms"][room]["exits"])
    return seen


def test_map_has_rooms():
    """The map must have at least 2 rooms for SAMPLE."""
    game_map = build_map(SAMPLE)
    assert len(game_map["rooms"]) >= 2


def test_all_rooms_and_boss_reachable():
    """Every room and the boss must be reachable from the start room."""
    game_map = build_map(SAMPLE)
    reachable = _reachable(game_map)
    assert reachable == set(game_map["rooms"])
    assert game_map["boss"] in reachable


def test_no_issues_still_gives_monsters():
    """When a repo has no issues, guardian monsters must still exist."""
    game_map = build_map(SAMPLE)
    assert len(game_map["monsters"]) >= 1
    # All monsters must be guardians (kind="guardian") when issues=[].
    for m in game_map["monsters"].values():
        assert m["kind"] == "guardian"
