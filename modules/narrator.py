"""
narrator.py — LLM narration with template fallback.

narrate(game, api_key, model_name) → game (with narration filled in)

One batch Gemini call using google-genai (not google-generativeai).
Model name comes from GEMINI_MODEL in .env — never hardcoded.
No temperature setting (deprecated for newer Flash models).
15-second timeout. 1 retry on validator failure. 0 retries on timeout.

Template strings for every game element live here (fallback when LLM fails).
narrated_by is set to "llm", "mixed", or "template".

Wired in: Step 8
"""


def narrate(game: dict, api_key: str, model_name: str) -> dict:
    """
    Add LLM narration to the game dict. Returns the updated game.
    Falls back to template text on any LLM failure.
    Implemented in Step 8.
    """
    raise NotImplementedError("narrator.narrate — implemented in Step 8")


# ---------------------------------------------------------------------------
# Template fallback text — used when the LLM fails or is unavailable.
# These strings are intentionally plain so they work without AI.
# ---------------------------------------------------------------------------

def _room_template(room_id: str, folder: str) -> str:
    name = folder if folder else "the entrance hall"
    return f"You are in {name}. Look around — exits lead onward."


def _monster_template(monster_id: str, monster: dict) -> str:
    return f"A creature blocks the way: {monster['title']}."


def _key_template(key_name: str, key: dict) -> str:
    return f"A key labelled '{key_name}' lies here. It came from {key['source']}."


def fill_templates(game: dict) -> dict:
    """
    Fill narration using plain template text. Returns updated game.
    Called when the LLM is unavailable entirely.
    """
    narration = {"rooms": {}, "monsters": {}, "keys": {}}
    for room_id, room in game["rooms"].items():
        narration["rooms"][room_id] = _room_template(room_id, room["folder"])
    for mid, monster in game["monsters"].items():
        narration["monsters"][mid] = _monster_template(mid, monster)
    for key_name, key in game["keys"].items():
        narration["keys"][key_name] = _key_template(key_name, key)
    game["narration"] = narration
    game["narrated_by"] = "template"
    return game
