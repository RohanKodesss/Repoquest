"""
quiz.py — Generate quiz questions from real repo data.

generate_quiz(game) → quiz dict

Quiz Type 1: "Which room holds file X?"
Quiz Type 2 (when repo has >= 4 dependencies): "Which of these is a real dependency of this project?"

Distractors are always real items sampled by code (never the LLM).
If repo has < 4 dependencies, falls back to Quiz Type 1.
No network calls. No LLM calls.
"""

from __future__ import annotations
import os
import random


def _make_room_question(game: dict, target_room_id: str, used_files: set[str]) -> dict:
    """Build a single 'Which room holds file X?' question object (Quiz Type #1)."""
    all_room_ids = list(game.get("rooms", {}).keys())
    target_room = game.get("rooms", {}).get(target_room_id, {})
    folder = target_room.get("folder", "")

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

    file_x = candidates[0]
    for c in candidates:
        if c not in used_files:
            file_x = c
            break
    used_files.add(file_x)

    answer = target_room_id
    other_rooms = [r for r in all_room_ids if r != answer]
    random.seed(42 + len(used_files))
    num_distractors = min(3, len(other_rooms))
    distractors = random.sample(other_rooms, num_distractors) if other_rooms else []

    options = [answer] + distractors
    random.shuffle(options)

    return {
        "type": "room_file",
        "question": f"Which room holds `{file_x}`?",
        "options": options,
        "answer": answer,
        "file": file_x,
    }


def _make_dependency_question(game: dict, used_deps: set[str]) -> dict | None:
    """
    Build a single 'Which of these is a real dependency of this project?' question (Quiz Type #2).
    Requires repo to have >= 4 dependencies.
    """
    dep_names = list(game.get("keys", {}).keys())
    if len(dep_names) < 4:
        return None  # Skip if < 4 dependencies, caller will fallback to Quiz Type #1

    # Pick answer dependency
    unused = [d for d in dep_names if d not in used_deps]
    answer = unused[0] if unused else dep_names[0]
    used_deps.add(answer)

    # Distractors: 3 other dependencies from the same repo
    other_deps = [d for d in dep_names if d != answer]
    random.seed(100 + len(used_deps))
    distractors = random.sample(other_deps, 3)

    options = [answer] + distractors
    random.shuffle(options)

    return {
        "type": "dependency",
        "question": "Which of these is a real dependency of this project?",
        "options": options,
        "answer": answer,
        "file": None,
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
    used_deps: set[str] = set()

    # Build map of monster_id -> room_id
    monster_room_map: dict[str, str] = {}
    for rid, rdata in game.get("rooms", {}).items():
        for mid in rdata.get("monsters", []):
            monster_room_map[mid] = rid

    dep_count = len(game.get("keys", {}))

    # Monster questions
    for idx, mid in enumerate(game.get("monsters", {}).keys()):
        # Alternate between Quiz Type 2 and Quiz Type 1 if dependencies >= 4
        if dep_count >= 4 and idx % 2 == 1:
            q_dep = _make_dependency_question(game, used_deps)
            if q_dep:
                monsters_quiz[mid] = q_dep
                continue

        target_room = monster_room_map.get(mid, game.get("start", "readme-hall"))
        monsters_quiz[mid] = _make_room_question(game, target_room, used_files)

    # Boss questions (3 sequential questions)
    boss_room_id = game.get("boss", game.get("start", "readme-hall"))
    boss_questions = [
        _make_room_question(game, boss_room_id, used_files),
        _make_room_question(game, boss_room_id, used_files),
        _make_room_question(game, boss_room_id, used_files),
    ]

    return {"monsters": monsters_quiz, "boss": boss_questions}
