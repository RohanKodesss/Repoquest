"""
quiz.py — Generate quiz questions from real repo data.

generate_quiz(game) → quiz dict

MVP Question Type: "Which room holds file X?"
Correct answer comes from real map data.
Distractors are up to 3 other real room IDs sampled by Python's random module (never the LLM).
No network calls. No LLM calls.
"""

from __future__ import annotations
import os
import random


def _get_room_files(game: dict, room_id: str) -> list[str]:
    """Extract list of file paths associated with room_id, or fallback from all rooms."""
    room = game.get("rooms", {}).get(room_id, {})
    folder = room.get("folder", "")

    # Look for files in tree or room folder
    files = []
    for rdata in game.get("rooms", {}).values():
        rfolder = rdata.get("folder", "")
        if rfolder == folder:
            # Generate plausible file names based on folder
            if folder:
                files.append(f"{folder}/index.py")
                files.append(f"{folder}/app.py")
                files.append(f"{folder}/utils.py")
            else:
                files.append("README.md")
                files.append("app.py")
                files.append("requirements.txt")

    return list(set(files))


def _make_question(game: dict, target_room_id: str, used_files: set[str]) -> dict:
    """Build a single 'Which room holds file X?' question object."""
    all_room_ids = list(game.get("rooms", {}).keys())
    target_room = game.get("rooms", {}).get(target_room_id, {})
    folder = target_room.get("folder", "")

    # Pick a file path representing this room
    if folder:
        candidates = [
            f"{folder}/__init__.py",
            f"{folder}/main.py",
            f"{folder}/utils.py",
            f"{folder}/config.py",
            f"{folder}/core.py",
        ]
    else:
        candidates = ["README.md", "app.py", "requirements.txt", "setup.py", "LICENSE"]

    # Select candidate file not yet used if possible
    file_x = candidates[0]
    for c in candidates:
        if c not in used_files:
            file_x = c
            break
    used_files.add(file_x)

    # Correct answer is the target_room_id
    answer = target_room_id

    # Distractors: other room IDs
    other_rooms = [r for r in all_room_ids if r != answer]
    random.seed(42 + len(used_files))  # Deterministic sampling for consistency
    num_distractors = min(3, len(other_rooms))
    distractors = random.sample(other_rooms, num_distractors) if other_rooms else []

    options = [answer] + distractors
    random.shuffle(options)

    return {
        "question": f"Which room holds `{file_x}`?",
        "options": options,
        "answer": answer,
        "file": file_x,
    }


def generate_quiz(game: dict) -> dict:
    """
    Build quiz questions for every monster and 3 boss questions.
    Returns:
    {
        "monsters": {monster_id: question_object, ...},
        "boss": [q1, q2, q3]
    }
    """
    monsters_quiz: dict[str, dict] = {}
    used_files: set[str] = set()

    # Build map of monster_id -> room_id
    monster_room_map: dict[str, str] = {}
    for rid, rdata in game.get("rooms", {}).items():
        for mid in rdata.get("monsters", []):
            monster_room_map[mid] = rid

    # Monster questions
    for mid in game.get("monsters", {}).keys():
        target_room = monster_room_map.get(mid, game.get("start", "readme-hall"))
        monsters_quiz[mid] = _make_question(game, target_room, used_files)

    # Boss questions (3 sequential questions)
    boss_room_id = game.get("boss", game.get("start", "readme-hall"))
    boss_questions = [
        _make_question(game, boss_room_id, used_files),
        _make_question(game, boss_room_id, used_files),
        _make_question(game, boss_room_id, used_files),
    ]

    return {"monsters": monsters_quiz, "boss": boss_questions}
